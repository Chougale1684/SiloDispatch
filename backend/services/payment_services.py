import os
import hmac
import hashlib
import json
import uuid
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models.models import Order, Delivery, CashLedger, Driver, PaymentStatus, PaymentMethod
from config.database import SessionLocal
from config.settings import CASHFREE_CONFIG

class PaymentService:
    def __init__(self):
        # Initialize with settings from both configurations
        self.cashfree_app_id = os.getenv("CASHFREE_APP_ID", CASHFREE_CONFIG.get('app_id', 'TEST_APP_ID'))
        self.cashfree_secret_key = os.getenv("CASHFREE_SECRET_KEY", CASHFREE_CONFIG.get('secret_key', 'TEST_SECRET_KEY'))
        self.cashfree_base_url = os.getenv("CASHFREE_BASE_URL", CASHFREE_CONFIG.get('base_url', 'https://sandbox.cashfree.com/pg'))
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", CASHFREE_CONFIG.get('webhook_secret', 'your_webhook_secret'))
        
    def generate_cashfree_headers(self) -> Dict[str, str]:
        """Generate headers for Cashfree API requests"""
        return {
            "x-client-id": self.cashfree_app_id,
            "x-client-secret": self.cashfree_secret_key,
            "Content-Type": "application/json"
        }
    
    def generate_upi_qr(self, order_data: dict) -> Dict[str, Any]:
        """Integrated UPI QR generation from both implementations"""
        # Extract required fields from order_data
        order_id = order_data.get('order_id', f"order_{uuid.uuid4().hex[:8]}")
        amount = order_data.get('amount', 0)
        customer_details = order_data.get('customer_details', {})
        
        # Create payment session first
        session_result = self.create_upi_payment_session(
            order_id=order_id,
            amount=amount,
            customer_details=customer_details
        )
        
        if not session_result.get('success'):
            return session_result
            
        # Then generate QR code
        qr_result = self._generate_upi_qr_code(
            session_result['payment_session_id'],
            amount,
            customer_details.get('customer_name', 'Customer')
        )
        
        return {
            **session_result,
            **qr_result
        }
    
    def _generate_upi_qr_code(self, payment_session_id: str, amount: float, customer_name: str) -> Dict[str, Any]:
        """Internal method to generate UPI QR code"""
        try:
            response = requests.get(
                f"{self.cashfree_base_url}/orders/{payment_session_id}/qrcode",
                headers=self.generate_cashfree_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "qr_code": result.get("qr_code"),
                    "upi_intent": result.get("upi_intent_url"),
                    "payment_session_id": payment_session_id
                }
            else:
                # Fallback QR generation
                return {
                    "qr_code": None,
                    "upi_intent": f"upi://pay?pa=merchant@upi&pn={customer_name}&mc=1234&tid={payment_session_id}&tr={payment_session_id}&am={amount}&cu=INR",
                    "payment_session_id": payment_session_id,
                    "warning": "Used fallback UPI intent as QR generation failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"QR generation failed: {str(e)}"
            }
    
    def create_upi_payment_session(self, order_id: str, amount: float, 
                                 customer_details: Dict[str, str]) -> Dict[str, Any]:
        """Create UPI payment session with Cashfree"""
        payload = {
            "order_id": order_id,
            "order_amount": amount,
            "order_currency": "INR",
            "customer_details": {
                "customer_id": customer_details.get("customer_id", f"cust_{uuid.uuid4().hex[:8]}"),
                "customer_name": customer_details.get("customer_name", "Customer"),
                "customer_email": customer_details.get("customer_email", "customer@example.com"),
                "customer_phone": customer_details.get("customer_phone", "9999999999")
            },
            "order_meta": {
                "return_url": f"{os.getenv('BASE_URL', 'http://localhost:8000')}/payment/return",
                "notify_url": f"{os.getenv('BASE_URL', 'http://localhost:8000')}/webhooks/payment"
            },
            "order_expiry_time": (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S+05:30"),
            "payment_methods": "upi"
        }
        
        try:
            response = requests.post(
                f"{self.cashfree_base_url}/orders",
                headers=self.generate_cashfree_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "payment_session_id": result.get("payment_session_id"),
                    "order_id": order_id,
                    "expires_at": payload["order_expiry_time"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Payment session creation failed: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Payment service error: {str(e)}"
            }
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Payment verification logic - integrates with existing webhook handling"""
        db = SessionLocal()
        
        try:
            # First check in our database (removed Payment model usage)
            # Directly check with Cashfree
            headers = self.generate_cashfree_headers()
            response = requests.get(
                f"{self.cashfree_base_url}/orders/{payment_id}/payments",
                headers=headers
            )
            
            if response.status_code == 200:
                payment_data = response.json()
                if payment_data and len(payment_data) > 0:
                    latest_payment = payment_data[0]
                    return {
                        "success": True,
                        "payment_id": payment_id,
                        "status": latest_payment.get("payment_status"),
                        "amount": latest_payment.get("payment_amount"),
                        "verified": latest_payment.get("payment_status") == "SUCCESS",
                        "source": "cashfree"
                    }
            
            return {
                "success": False,
                "error": "Payment not found",
                "payment_id": payment_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "payment_id": payment_id
            }
        finally:
            db.close()

    # Include all other existing methods exactly as they were:
    # - verify_webhook_signature()
    # - handle_payment_webhook() 
    # - record_cash_payment()
    # - get_driver_cash_balance()
    # - settle_driver_cash()
    # - get_payment_analytics()
    # - process_prepaid_order()
    # (Keep all these methods unchanged from your original implementation)

# Example usage
if __name__ == "__main__":
    payment_service = PaymentService()
    
    # Test integrated QR generation
    qr_result = payment_service.generate_upi_qr({
        "order_id": "test_order_456",
        "amount": 1500.50,
        "customer_details": {
            "customer_name": "Test User",
            "customer_phone": "9876543210"
        }
    })
    print("QR Generation Result:", qr_result)
    
    # Test payment verification
    verification = payment_service.verify_payment("test_payment_123")
    print("Payment Verification:", verification)