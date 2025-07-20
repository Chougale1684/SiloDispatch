from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import random

from config.database import get_db
from models.models import Delivery, Order
from services.notification_services import send_otp_notification

router = APIRouter()

@router.post("/deliveries/{delivery_id}/arrived")
def mark_arrived(delivery_id: str, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    # Generate 6-digit OTP
    otp = f"{random.randint(100000, 999999)}"
    delivery.otp = otp
    delivery.otp_generated_at = datetime.utcnow()
    db.commit()
    # Send OTP to customer (mocked)
    order = db.query(Order).filter(Order.id == delivery.order_id).first()
    if order:
        send_otp_notification(order.customer_phone, otp)
    return {"message": "OTP sent to customer"}

@router.post("/deliveries/{delivery_id}/verify-otp")
def verify_otp(delivery_id: str, otp: str, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery or delivery.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    delivery.otp_verified_at = datetime.utcnow()
    db.commit()
    return {"message": "OTP verified, payment collection unlocked"}

@router.post("/deliveries/{delivery_id}/collect-payment")
def collect_payment(delivery_id: str, db: Session = Depends(get_db)):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    if not delivery.otp_verified_at:
        raise HTTPException(status_code=403, detail="OTP not verified. Payment collection is locked.")
    # ... your payment collection logic here ...
    return {"message": "Payment collected"}