# api/routes/payments.py
from fastapi import APIRouter, Depends, HTTPException
from services.payment_services import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])
payment_service = PaymentService()

@router.post("/upi-qr")
async def generate_upi_qr(order_data: dict):
    return payment_service.generate_upi_qr(order_data)

@router.get("/verify/{payment_id}")
async def verify_payment(payment_id: str):
    return payment_service.verify_payment(payment_id)