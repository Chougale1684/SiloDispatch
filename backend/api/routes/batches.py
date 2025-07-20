from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from config.database import get_db
from models.models import Order, Batch, OrderStatus
from utils.clustering import create_optimized_batches

router = APIRouter(prefix="/batches", tags=["Batches"])

class BatchResponse(BaseModel):
    id: str
    created_at: datetime
    status: str
    current_weight: float
    current_orders: int
    estimated_distance: Optional[float] = None
    center_latitude: Optional[float] = None
    center_longitude: Optional[float] = None

class BatchCreateRequest(BaseModel):
    algorithm: Optional[str] = "kmeans"
    max_weight: Optional[float] = 25.0
    max_orders: Optional[int] = 30
    order_ids: Optional[List[str]] = None

@router.post("/create", response_model=List[BatchResponse])
async def create_batches(request: BatchCreateRequest, db: Session = Depends(get_db)):
    if request.order_ids:
        orders = db.query(Order).filter(Order.id.in_(request.order_ids)).all()
    else:
        orders = db.query(Order).filter(Order.status == OrderStatus.PENDING.value).all()
    
    if not orders:
        raise HTTPException(status_code=400, detail="No orders available for batching")
    
    batch_data = create_optimized_batches(
        orders, 
        algorithm=request.algorithm,
        max_weight=request.max_weight,
        max_orders=request.max_orders
    )
    
    created_batches = []
    for batch_info in batch_data:
        batch = Batch(
            id=batch_info['id'],
            current_weight=batch_info['total_weight'],
            current_orders=batch_info['total_orders'],
            estimated_distance=batch_info.get('estimated_distance'),
            center_latitude=batch_info.get('center_latitude'),
            center_longitude=batch_info.get('center_longitude'),
            max_weight=request.max_weight,
            max_orders=request.max_orders
        )
        db.add(batch)
        for order in batch_info['orders']:
            order.batch_id = batch.id
            order.status = OrderStatus.BATCHED.value
        created_batches.append(batch)
    
    db.commit()
    return created_batches

@router.get("/", response_model=List[BatchResponse])
async def get_batches(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Batch)
    if status:
        query = query.filter(Batch.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/today")
async def get_today_batches(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    batches = db.query(Batch).filter(
        Batch.created_at >= today,
        Batch.created_at < today + timedelta(days=1)
    ).all()
    return {
        "date": today.isoformat(),
        "total_batches": len(batches),
        "batches": batches
    }