# ~/silo_fortune/services/payment_webhook_service.py
import json
from sqlalchemy.orm import Session
from models.models import Order, Payment
from config.database import SessionLocal

def process_payment_webhook(payload: bytes):
    data = json.loads(payload)
    db = SessionLocal()
    
    try:
        order = db.query(Order).filter(Order.id == data["order_id"]).first()
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        # Update payment status
        payment = Payment(
            order_id=order.id,
            amount=data["amount"],
            status=data["payment_status"],
            provider_data=payload.decode()
        )
        db.add(payment)
        db.commit()
        
        return {"status": "success"}
    finally:
        db.close()