# services/order_service.py
from sqlalchemy.orm import Session
from models import Order, OrderStatus
from typing import List, Optional
import uuid
import csv
import io
import json

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order_data: dict) -> Order:
        """Create a new order"""
        order = Order(
            id=str(uuid.uuid4()),
            **order_data
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def get_orders(self, skip: int = 0, limit: int = 100, 
                   status: Optional[str] = None) -> List[Order]:
        """Get orders with optional filtering"""
        query = self.db.query(Order)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.offset(skip).limit(limit).all()

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        return self.db.query(Order).filter(Order.id == order_id).first()

    def update_order(self, order_id: str, update_data: dict) -> Optional[Order]:
        """Update an order"""
        order = self.get_order_by_id(order_id)
        if not order:
            return None
        
        for field, value in update_data.items():
            if hasattr(order, field):
                setattr(order, field, value)
        
        self.db.commit()
        self.db.refresh(order)
        return order

    def delete_order(self, order_id: str) -> bool:
        """Delete an order"""
        order = self.get_order_by_id(order_id)
        if not order:
            return False
        
        self.db.delete(order)
        self.db.commit()
        return True

    def get_pending_orders(self) -> List[Order]:
        """Get all pending orders"""
        return self.db.query(Order).filter(
            Order.status == OrderStatus.PENDING.value
        ).all()

    def get_orders_by_ids(self, order_ids: List[str]) -> List[Order]:
        """Get orders by list of IDs"""
        return self.db.query(Order).filter(Order.id.in_(order_ids)).all()

    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status"""
        order = self.get_order_by_id(order_id)
        if not order:
            return False
        
        order.status = status
        self.db.commit()
        return True

    def assign_orders_to_batch(self, order_ids: List[str], batch_id: str) -> bool:
        """Assign orders to a batch"""
        orders = self.get_orders_by_ids(order_ids)
        
        for order in orders:
            order.batch_id = batch_id
            order.status = OrderStatus.BATCHED.value
        
        self.db.commit()
        return True

    def import_orders_from_csv(self, csv_content: str) -> dict:
        """Import orders from CSV content"""
        csv_data = io.StringIO(csv_content)
        reader = csv.DictReader(csv_data)
        
        orders_created = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=1):
            try:
                # Parse items JSON
                items = json.loads(row.get('items', '[]'))
                
                order_data = {
                    'customer_name': row['customer_name'],
                    'customer_phone': row['customer_phone'],
                    'customer_address': row['customer_address'],
                    'pincode': row['pincode'],
                    'latitude': float(row['latitude']),
                    'longitude': float(row['longitude']),
                    'items': items,
                    'total_weight': float(row['total_weight']),
                    'total_amount': float(row['total_amount']),
                    'delivery_slot': row.get('delivery_slot'),
                    'payment_method': row.get('payment_method', 'cash')
                }
                
                self.create_order(order_data)
                orders_created += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return {
            "orders_created": orders_created,
            "errors": errors,
            "total_rows": row_num if 'row_num' in locals() else 0
        }

    def get_orders_by_pincode(self, pincode: str) -> List[Order]:
        """Get orders by pincode"""
        return self.db.query(Order).filter(Order.pincode == pincode).all()

    def get_orders_statistics(self) -> dict:
        """Get order statistics"""
        total_orders = self.db.query(Order).count()
        pending_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.PENDING.value
        ).count()
        batched_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.BATCHED.value
        ).count()
        delivered_orders = self.db.query(Order).filter(
            Order.status == OrderStatus.DELIVERED.value
        ).count()
        
        return {
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "batched_orders": batched_orders,
            "delivered_orders": delivered_orders
        }