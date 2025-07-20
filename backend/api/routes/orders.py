from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
import uuid
from datetime import datetime
import json
from pydantic import BaseModel
from config.database import get_db
from models.models import Order

router = APIRouter(prefix="/orders", tags=["Orders"])

# Pydantic models
class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_address: str
    pincode: str
    latitude: float
    longitude: float
    items: List[dict]
    total_weight: float
    total_amount: float
    delivery_slot: Optional[str] = None
    payment_method: Optional[str] = "cash"

class OrderResponse(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    customer_address: str
    pincode: str
    latitude: float
    longitude: float
    items: List[dict]
    total_weight: float
    total_amount: float
    status: str
    created_at: datetime
    batch_id: Optional[str] = None

@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(
        id=str(uuid.uuid4()),
        **order.dict()
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderResponse])
async def get_orders(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.post("/import-csv")
async def import_orders_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    contents = await file.read()
    csv_data = io.StringIO(contents.decode('utf-8'))
    reader = csv.DictReader(csv_data)
    
    orders_created = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=1):
        try:
            items = json.loads(row.get('items', '[]'))
            order = Order(
                id=str(uuid.uuid4()),
                customer_name=row['customer_name'],
                customer_phone=row['customer_phone'],
                customer_address=row['customer_address'],
                pincode=row['pincode'],
                latitude=float(row['latitude']),
                longitude=float(row['longitude']),
                items=items,
                total_weight=float(row['total_weight']),
                total_amount=float(row['total_amount']),
                delivery_slot=row.get('delivery_slot'),
                payment_method=row.get('payment_method', 'cash')
            )
            db.add(order)
            orders_created += 1
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    if orders_created > 0:
        db.commit()
    
    return {
        "orders_created": orders_created,
        "errors": errors,
        "total_rows": row_num if 'row_num' in locals() else 0
    }