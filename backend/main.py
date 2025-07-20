from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
import uuid
from datetime import datetime, timedelta
import json
from pydantic import BaseModel

# Import your existing API routes (you'll need to create this)
from api.routes import orders, batches, drivers  # Example imports

# Database setup
from config.database import Base, engine, get_db, create_tables
from models.models import Order, Batch, Driver, OrderStatus, BatchStatus
from utils.clustering import create_optimized_batches

# main.py (add these imports)
from api.routes.payments import router as payments_router
from api.routes.notifications import router as notifications_router

# ~/silo_fortune/main.py
from api.routes.payment_webhooks import router as webhook_router
from api.routes.payments import router as payments_router
from api.routes.deliveries import router as deliveries_router

# app = FastAPI()


# Create FastAPI app
app = FastAPI(
    title="SiloDispatch API",
    description="Smart Last-Mile Logistics Platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your API routers (you'll need to organize your routes into separate files)
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(batches.router, prefix="/batches", tags=["batches"])
app.include_router(drivers.router, prefix="/drivers", tags=["drivers"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
app.include_router(webhook_router)  # Add this line with other routers
app.include_router(deliveries_router, prefix="/deliveries", tags=["deliveries"])

# Pydantic models for request/response
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

# Startup event
# @app.on_event("startup")
# async def startup_event():
#     Base.metadata.create_all(bind=engine)

# Health check endpoint
@app.get("/health")
async def health_check():
    from datetime import datetime
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# Order endpoints
@app.post("/orders", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order"""
    db_order = Order(
        id=str(uuid.uuid4()),
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        customer_address=order.customer_address,
        pincode=order.pincode,
        latitude=order.latitude,
        longitude=order.longitude,
        items=order.items,
        total_weight=order.total_weight,
        total_amount=order.total_amount,
        delivery_slot=order.delivery_slot,
        payment_method=order.payment_method
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return db_order

@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(skip: int = 0, limit: int = 100, status: Optional[str] = None, 
                    db: Session = Depends(get_db)):
    """Get all orders with optional filtering"""
    query = db.query(Order)
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get a specific order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(order_id: str, order_update: OrderCreate, db: Session = Depends(get_db)):
    """Update an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    for field, value in order_update.dict().items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    return order

@app.delete("/orders/{order_id}")
async def delete_order(order_id: str, db: Session = Depends(get_db)):
    """Delete an order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}

# CSV Import endpoint
@app.post("/orders/import-csv")
async def import_orders_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import orders from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    contents = await file.read()
    csv_data = io.StringIO(contents.decode('utf-8'))
    reader = csv.DictReader(csv_data)
    
    orders_created = 0
    errors = []
    
    for row_num, row in enumerate(reader, start=1):
        try:
            # Parse items JSON
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

# Webhook endpoint for order creation
@app.post("/webhooks/orders")
async def order_webhook(orders: List[OrderCreate], db: Session = Depends(get_db)):
    """Webhook endpoint to receive orders from external systems"""
    created_orders = []
    
    for order_data in orders:
        order = Order(
            id=str(uuid.uuid4()),
            **order_data.dict()
        )
        db.add(order)
        created_orders.append(order)
    
    db.commit()
    
    return {
        "message": f"Successfully created {len(created_orders)} orders",
        "order_ids": [order.id for order in created_orders]
    }

# Batch endpoints
@app.post("/batches/create", response_model=List[BatchResponse])
async def create_batches(request: BatchCreateRequest, db: Session = Depends(get_db)):
    """Create batches from pending orders"""
    
    # Get orders to batch
    if request.order_ids:
        orders = db.query(Order).filter(Order.id.in_(request.order_ids)).all()
    else:
        orders = db.query(Order).filter(Order.status == OrderStatus.PENDING.value).all()
    
    if not orders:
        raise HTTPException(status_code=400, detail="No orders available for batching")
    
    # Create batches using clustering algorithm
    batch_data = create_optimized_batches(
        orders, 
        algorithm=request.algorithm,
        max_weight=request.max_weight,
        max_orders=request.max_orders
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
            max_weight=request.max_weight,
            max_orders=request.max_orders
        )
        
        db.add(batch)
        
        # Update orders with batch_id and status
        for order in batch_info['orders']:
            order.batch_id = batch.id
            order.status = OrderStatus.BATCHED.value
        
        created_batches.append(batch)
    
    db.commit()
    
    return created_batches

@app.get("/batches", response_model=List[BatchResponse])
async def get_batches(skip: int = 0, limit: int = 100, status: Optional[str] = None, 
                     db: Session = Depends(get_db)):
    """Get all batches with optional filtering"""
    query = db.query(Batch)
    
    if status:
        query = query.filter(Batch.status == status)
    
    batches = query.offset(skip).limit(limit).all()
    return batches

@app.get("/batches/{batch_id}", response_model=BatchResponse)
async def get_batch(batch_id: str, db: Session = Depends(get_db)):
    """Get a specific batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch

@app.get("/batches/{batch_id}/orders", response_model=List[OrderResponse])
async def get_batch_orders(batch_id: str, db: Session = Depends(get_db)):
    """Get all orders in a batch"""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    orders = db.query(Order).filter(Order.batch_id == batch_id).all()
    return orders

@app.get("/batches/today")
async def get_today_batches(db: Session = Depends(get_db)):
    """Get today's batches endpoint"""
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

# Driver endpoints
@app.get("/drivers")
async def get_drivers(db: Session = Depends(get_db)):
    """Get all drivers"""
    drivers = db.query(Driver).all()
    return drivers

@app.post("/drivers")
async def create_driver(name: str, phone: str, vehicle_type: str, 
                       vehicle_number: str, db: Session = Depends(get_db)):
    """Create a new driver"""
    driver = Driver(
        id=str(uuid.uuid4()),
        name=name,
        phone=phone,
        vehicle_type=vehicle_type,
        vehicle_number=vehicle_number
    )
    
    db.add(driver)
    db.commit()
    db.refresh(driver)
    
    return driver

# Statistics endpoint
@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING.value).count()
    total_batches = db.query(Batch).count()
    available_drivers = db.query(Driver).filter(Driver.status == "available").count()
    
    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_batches": total_batches,
        "available_drivers": available_drivers,
        "timestamp": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)