from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from config.database import get_db
from models.models import Driver

router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.get("/")
async def get_drivers(db: Session = Depends(get_db)):
    return db.query(Driver).all()

@router.post("/")
async def create_driver(name: str, phone: str, vehicle_type: str, vehicle_number: str, db: Session = Depends(get_db)):
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