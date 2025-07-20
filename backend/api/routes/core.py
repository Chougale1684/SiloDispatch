from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from config.database import get_db
from models.models import Order, Batch, Driver, OrderStatus
from services.batch_processing import BatchProcessor
from config.database import Base, engine

router = APIRouter(tags=["Core API"])

# Initialize scheduler
scheduler = BackgroundScheduler()
batch_processor = BatchProcessor()

def start_scheduler():
    """Start background scheduler"""
    if not scheduler.running:
        scheduler.start()
        print("Scheduler started")

@router.on_event("startup")
async def startup_event():
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    # Start scheduler with db session
    db = next(get_db())  # Get a DB session
    scheduler.add_job(
        batch_processor.auto_create_batches,
        'interval',
        hours=1,
        args=[db]
    )
    start_scheduler()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow(),
        "scheduler_running": scheduler.running
    }

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Existing stats endpoint"""
    ...

    # Add this temporary endpoint to core.py
@router.get("/db-check")
async def database_check(db: Session = Depends(get_db)):
    return {
        "orders_count": db.query(Order).count(),
        "latest_batch": db.query(Batch).order_by(Batch.created_at.desc()).first(),
        "active_drivers": db.query(Driver).filter(Driver.status == "active").count()
    }