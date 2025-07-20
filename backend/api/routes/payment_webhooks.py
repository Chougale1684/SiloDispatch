# ~/silo_fortune/api/routes/payment_webhooks.py
from fastapi import APIRouter, Request, HTTPException
from scripts.webhooks import webhook_verifier
from services.payment_webhook_services import process_payment_webhook

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/payments")
async def handle_payment(request: Request):
    payload = await request.body()
    signature = request.headers.get("X-Cashfree-Signature")
    
    if not webhook_verifier.verify(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    return await process_payment_webhook(payload)