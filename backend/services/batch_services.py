# services/batch_service.py
from sqlalchemy.orm import Session
from models import Batch, Order, BatchStatus, OrderStatus
from utils.clustering import create_optimized_batches
from typing import List, Optional
import uuid
from datetime import datetime, timedelta

class BatchService:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, batch_data: dict) -> Batch:
        """Create a new batch"""
        batch = Batch(
            id=str(uuid.uuid4()),
            **batch_data
        )
        self.db.add(batch)
        self.db.commit()
        self.db.refresh(batch)
        return batch

    def get_batches(self, skip: int = 0, limit: int = 100, 
                    status: Optional[str] = None) -> List[Batch]:
        """Get batches with optional filtering"""
        query = self.db.query(Batch)
        
        if status:
            query = query.filter(Batch.status == status)
        
        return query.offset(skip).limit(limit).all()

    def get_batch_by_id(self, batch_id: str) -> Optional[Batch]:
        """Get batch by ID"""
        return self.db.query(Batch).filter(Batch.id == batch_id).first()

    def get_batch_orders(self, batch_id: str) -> List[Order]:
        """Get all orders in a batch"""
        return self.db.query(Order).filter(Order.batch_id == batch_id).all()

    def create_batches_from_orders(self, orders: List[Order], 
                                  algorithm: str = "kmeans",
                                  max_weight: float = 25.0,
                                  max_orders: int = 30) -> List[Batch]:
        """Create batches from orders using clustering algorithm"""
        if not orders:
            return []
        
        # Use clustering algorithm to create optimal batches
        batch_data = create_optimized_batches(
            orders, 
            algorithm=algorithm,
            max_weight=max_weight,
            max_orders=max_orders
        )
        
        created_batches = []
        
        for batch_info in batch_data:
            # Create batch record
            batch = Batch(
                id=batch_info['id'],
                current_weight=batch_info['total_weight'],
                current_orders=batch_info['total_orders'],
                estimated_distance=batch_info.get('estimated_distance'),
                center_latitude=batch_info.get('center_latitude'),
                center_longitude=batch_info.get('center_longitude'),
                max_weight=max_weight,
                max_orders=max_orders
            )
            
            self.db.add(batch)
            
            # Update orders with batch_id and status
            for order in batch_info['orders']:
                order.batch_id = batch.id
                order.status = OrderStatus.BATCHED.value
            
            created_batches.append(batch)
        
        self.db.commit()
        return created_batches

    def create_batches_from_pending_orders(self, algorithm: str = "kmeans",
                                         max_weight: float = 25.0,
                                         max_orders: int = 30) -> List[Batch]:
        """Create batches from all pending orders"""
        pending_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.PENDING.value
        ).all()
        
        return self.create_batches_from_orders(
            pending_orders, algorithm, max_weight, max_orders
        )

    def assign_batch_to_driver(self, batch_id: str, driver_id: str) -> bool:
        """Assign a batch to a driver"""
        batch = self.get_batch_by_id(batch_id)
        if not batch:
            return False
        
        batch.driver_id = driver_id
        batch.status = BatchStatus.ASSIGNED.value
        
        # Update all orders in the batch
        orders = self.get_batch_orders(batch_id)
        for order in orders:
            order.status = OrderStatus.ASSIGNED.value
        
        self.db.commit()
        return True

    def start_batch_delivery(self, batch_id: str) -> bool:
        """Mark batch as in progress"""
        batch = self.get_batch_by_id(batch_id)
        if not batch:
            return False
        
        batch.status = BatchStatus.IN_PROGRESS.value
        
        # Update all orders in the batch
        orders = self.get_batch_orders(batch_id)
        for order in orders:
            order.status = OrderStatus.OUT_FOR_DELIVERY.value
        
        self.db.commit()
        return True

    def complete_batch(self, batch_id: str) -> bool:
        """Mark batch as completed"""
        batch = self.get_batch_by_id(batch_id)
        if not batch:
            return False
        
        batch.status = BatchStatus.COMPLETED.value
        self.db.commit()
        return True

    def get_today_batches(self) -> List[Batch]:
        """Get today's batches"""
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)
        
        return self.db.query(Batch).filter(
            Batch.created_at >= today,
            Batch.created_at < tomorrow
        ).all()

    def get_batches_by_driver(self, driver_id: str) -> List[Batch]:
        """Get batches assigned to a specific driver"""
        return self.db.query(Batch).filter(Batch.driver_id == driver_id).all()

    def get_batch_statistics(self) -> dict:
        """Get batch statistics"""
        total_batches = self.db.query(Batch).count()
        created_batches = self.db.query(Batch).filter(
            Batch.status == BatchStatus.CREATED.value
        ).count()
        assigned_batches = self.db.query(Batch).filter(
            Batch.status == BatchStatus.ASSIGNED.value
        ).count()
        in_progress_batches = self.db.query(Batch).filter(
            Batch.status == BatchStatus.IN_PROGRESS.value
        ).count()
        completed_batches = self.db.query(Batch).filter(
            Batch.status == BatchStatus.COMPLETED.value
        ).count()
        
        return {
            "total_batches": total_batches,
            "created_batches": created_batches,
            "assigned_batches": assigned_batches,
            "in_progress_batches": in_progress_batches,
            "completed_batches": completed_batches
        }

    def calculate_total_distance_saved(self) -> dict:
        """Calculate total distance saved by batching"""
        batches = self.db.query(Batch).all()
        
        total_optimized_distance = sum(batch.estimated_distance or 0 for batch in batches)
        
        # Calculate naive distance (individual delivery for each order)
        total_naive_distance = 0
        for batch in batches:
            orders = self.get_batch_orders(batch.id)
            # Assume each order would require a round trip from depot
            # This is a simplified calculation - you could make it more sophisticated
            total_naive_distance += len(orders) * 10  # Assume 10km average per order
        
        distance_saved = total_naive_distance - total_optimized_distance
        savings_percentage = (distance_saved / total_naive_distance * 100) if total_naive_distance > 0 else 0
        
        return {
            "total_optimized_distance": total_optimized_distance,
            "total_naive_distance": total_naive_distance,
            "distance_saved": distance_saved,
            "savings_percentage": round(savings_percentage, 2)
        }

    def get_batch_efficiency_metrics(self, batch_id: str) -> dict:
        """Get efficiency metrics for a specific batch"""
        batch = self.get_batch_by_id(batch_id)
        if not batch:
            return {}
        
        orders = self.get_batch_orders(batch_id)
        
        # Calculate metrics
        weight_utilization = (batch.current_weight / batch.max_weight) * 100
        order_utilization = (batch.current_orders / batch.max_orders) * 100
        
        return {
            "batch_id": batch_id,
            "weight_utilization": round(weight_utilization, 2),
            "order_utilization": round(order_utilization, 2),
            "estimated_distance": batch.estimated_distance,
            "total_orders": len(orders),
            "total_weight": batch.current_weight,
            "status": batch.status
        }