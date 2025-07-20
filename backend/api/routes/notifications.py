# api/routes/notifications.py
from fastapi import APIRouter
from services.notification_services import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
notification_service = NotificationService()

@router.post("/otp/{order_id}")
async def send_otp(order_id: str, phone: str):
    return notification_service.generate_and_send_otp(order_id, phone)

@router.post("/delivery-update/{order_id}")
async def send_delivery_update(order_id: str, notification_type: str):
    return notification_service.send_delivery_notification(order_id, notification_type)