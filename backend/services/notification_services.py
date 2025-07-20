# services/notification_service.py
import os
import requests
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from models.models import Order, Driver, Delivery
from config.database import SessionLocal

def send_otp_notification(phone: str, otp: str):
    # Replace this with real SMS/WhatsApp integration
        print(f"Sending OTP {otp} to {phone}")

class NotificationService:
    def __init__(self):
        # SMS Service Configuration (using multiple providers for reliability)
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # MSG91 Configuration (Indian SMS provider)
        self.msg91_auth_key = os.getenv("MSG91_AUTH_KEY", "your_msg91_auth_key")
        self.msg91_sender_id = os.getenv("MSG91_SENDER_ID", "SILODP")
        
        # AWS SNS Configuration
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "ap-south-1")
        
        # WhatsApp Business API (optional)
        self.whatsapp_token = os.getenv("WHATSAPP_TOKEN")
        self.whatsapp_phone_id = os.getenv("WHATSAPP_PHONE_ID")
        
        # Email Configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        # OTP Configuration
        self.otp_length = 6
        self.otp_expiry_minutes = 10
        
    def generate_otp(self) -> str:
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=self.otp_length))
    
    def send_sms_twilio(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using Twilio"""
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
            return {"success": False, "error": "Twilio credentials not configured"}
        
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message = client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=phone_number
            )
            
            return {
                "success": True,
                "message_id": message.sid,
                "provider": "twilio"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_sms_msg91(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using MSG91 (Indian provider)"""
        if not self.msg91_auth_key:
            return {"success": False, "error": "MSG91 credentials not configured"}
        
        try:
            # Remove country code if present
            if phone_number.startswith('+91'):
                phone_number = phone_number[3:]
            elif phone_number.startswith('91'):
                phone_number = phone_number[2:]
            
            url = "https://api.msg91.com/api/sendhttp.php"
            
            params = {
                'authkey': self.msg91_auth_key,
                'mobiles': phone_number,
                'message': message,
                'sender': self.msg91_sender_id,
                'route': '4',  # Transactional route
                'country': '91'
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message_id": response.text,
                    "provider": "msg91"
                }
            else:
                return {"success": False, "error": f"MSG91 API error: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_sms_aws_sns(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using AWS SNS"""
        if not all([self.aws_access_key, self.aws_secret_key]):
            return {"success": False, "error": "AWS credentials not configured"}
        
        try:
            import boto3
            
            sns_client = boto3.client(
                'sns',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            
            response = sns_client.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            
            return {
                "success": True,
                "message_id": response['MessageId'],
                "provider": "aws_sns"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_sms(self, phone_number: str, message: str, preferred_provider: str = "msg91") -> Dict[str, Any]:
        """Send SMS with fallback providers"""
        
        # Ensure phone number has country code
        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number.lstrip('0')
        
        providers = {
            "msg91": self.send_sms_msg91,
            "twilio": self.send_sms_twilio,
            "aws_sns": self.send_sms_aws_sns
        }
        
        # Try preferred provider first
        if preferred_provider in providers:
            result = providers[preferred_provider](phone_number, message)
            if result["success"]:
                return result
        
        # Fallback to other providers
        for provider_name, provider_func in providers.items():
            if provider_name != preferred_provider:
                result = provider_func(phone_number, message)
                if result["success"]:
                    return result
        
        return {"success": False, "error": "All SMS providers failed"}
    
    def send_whatsapp_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp message using Business API"""
        if not all([self.whatsapp_token, self.whatsapp_phone_id]):
            return {"success": False, "error": "WhatsApp credentials not configured"}
        
        try:
            url = f"https://graph.facebook.com/v18.0/{self.whatsapp_phone_id}/messages"
            
            headers = {
                'Authorization': f'Bearer {self.whatsapp_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message_id": response.json().get('messages', [{}])[0].get('id'),
                    "provider": "whatsapp"
                }
            else:
                return {"success": False, "error": f"WhatsApp API error: {response.text}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> Dict[str, Any]:
        """Send email notification"""
        if not all([self.smtp_username, self.smtp_password]):
            return {"success": False, "error": "Email credentials not configured"}
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return {"success": True, "message": "Email sent successfully"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_and_send_otp(self, order_id: str, phone_number: str) -> Dict[str, Any]:
        """Generate OTP and send to customer"""
        db = SessionLocal()
        
        try:
            # Find delivery record
            delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
            if not delivery:
                return {"success": False, "error": "Delivery record not found"}
            
            # Generate OTP
            otp = self.generate_otp()
            
            # Update delivery record
            delivery.otp = otp
            delivery.otp_generated_at = datetime.utcnow()
            
            db.commit()
            
            # Send OTP via SMS
            message = f"Your OTP for SiloDispatch delivery is: {otp}. Valid for {self.otp_expiry_minutes} minutes. Do not share this OTP."
            
            sms_result = self.send_sms(phone_number, message)
            
            if sms_result["success"]:
                return {
                    "success": True,
                    "message": "OTP sent successfully",
                    "otp_id": delivery.id,
                    "expires_at": (datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)).isoformat()
                }
            else:
                return {"success": False, "error": f"Failed to send OTP: {sms_result['error']}"}
                
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def verify_otp(self, order_id: str, otp: str) -> Dict[str, Any]:
        """Verify OTP for delivery"""
        db = SessionLocal()
        
        try:
            # Find delivery record
            delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
            if not delivery:
                return {"success": False, "error": "Delivery record not found"}
            
            # Check if OTP matches
            if delivery.otp != otp:
                return {"success": False, "error": "Invalid OTP"}
            
            # Check if OTP is expired
            if not delivery.otp_generated_at:
                return {"success": False, "error": "OTP not generated"}
            
            expiry_time = delivery.otp_generated_at + timedelta(minutes=self.otp_expiry_minutes)
            if datetime.utcnow() > expiry_time:
                return {"success": False, "error": "OTP expired"}
            
            # Mark OTP as verified
            delivery.otp_verified_at = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "message": "OTP verified successfully",
                "verified_at": delivery.otp_verified_at.isoformat()
            }
            
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def send_delivery_notification(self, order_id: str, notification_type: str) -> Dict[str, Any]:
        """Send delivery status notifications"""
        db = SessionLocal()
        
        try:
            # Get order and delivery details
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {"success": False, "error": "Order not found"}
            
            delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
            driver = db.query(Driver).filter(Driver.id == delivery.driver_id).first() if delivery else None
            
            # Generate message based on notification type
            messages = {
                "order_assigned": f"Your order {order_id[:8]} has been assigned to our delivery partner {driver.name if driver else 'N/A'}. Expected delivery today.",
                "out_for_delivery": f"Your order {order_id[:8]} is out for delivery. Our delivery partner {driver.name if driver else 'N/A'} will reach you soon.",
                "nearby": f"Your delivery partner {driver.name if driver else 'N/A'} is nearby. Please be available at {order.customer_address}",
                "delivered": f"Your order {order_id[:8]} has been delivered successfully. Thank you for choosing SiloDispatch!"
            }
            
            message = messages.get(notification_type, f"Order {order_id[:8]} status update")
            
            # Send SMS notification
            sms_result = self.send_sms(order.customer_phone, message)
            
            # Also try WhatsApp if available
            whatsapp_result = self.send_whatsapp_message(order.customer_phone, message)
            
            return {
                "success": True,
                "message": "Notifications sent",
                "sms_result": sms_result,
                "whatsapp_result": whatsapp_result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def send_driver_notification(self, driver_id: str, message: str) -> Dict[str, Any]:
        """Send notification to driver"""
        db = SessionLocal()
        
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                return {"success": False, "error": "Driver not found"}
            
            # Send SMS to driver
            sms_result = self.send_sms(driver.phone, message)
            
            return {
                "success": True,
                "message": "Driver notification sent",
                "sms_result": sms_result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def send_batch_assignment_notification(self, batch_id: str, driver_id: str) -> Dict[str, Any]:
        """Send batch assignment notification to driver"""
        db = SessionLocal()
        
        try:
            from models import Batch
            
            batch = db.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                return {"success": False, "error": "Batch not found"}
            
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                return {"success": False, "error": "Driver not found"}
            
            # Count orders in batch
            order_count = db.query(Order).filter(Order.batch_id == batch_id).count()
            
            # Generate message
            message = f"New batch assigned! Batch ID: {batch_id[:8]}, Orders: {order_count}. Please check your app for delivery details."
            
            # Send SMS to driver
            sms_result = self.send_sms(driver.phone, message)
            
            return {
                "success": True,
                "message": "Batch assignment notification sent",
                "sms_result": sms_result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def send_emergency_notification(self, driver_id: str, order_id: str = None) -> Dict[str, Any]:
        """Send emergency notification to admin and relevant parties"""
        db = SessionLocal()
        
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                return {"success": False, "error": "Driver not found"}
            
            # Generate emergency message
            if order_id:
                message = f"EMERGENCY: Driver {driver.name} ({driver.phone}) has triggered emergency alert for order {order_id[:8]}. Immediate attention required!"
            else:
                message = f"EMERGENCY: Driver {driver.name} ({driver.phone}) has triggered emergency alert. Immediate attention required!"
            
            # Send to admin numbers (hardcoded for now, could be in config)
            admin_numbers = [
                "+918888888888",  # Replace with actual admin numbers
                "+917777777777"
            ]
            
            results = []
            for admin_phone in admin_numbers:
                sms_result = self.send_sms(admin_phone, message)
                results.append(sms_result)
            
            return {
                "success": True,
                "message": "Emergency notifications sent",
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def send_bulk_notification(self, recipient_type: str, message: str, filter_criteria: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send bulk notifications to drivers or customers"""
        db = SessionLocal()
        
        try:
            recipients = []
            
            if recipient_type == "drivers":
                query = db.query(Driver)
                if filter_criteria:
                    if "status" in filter_criteria:
                        query = query.filter(Driver.status == filter_criteria["status"])
                    if "city" in filter_criteria:
                        query = query.filter(Driver.city == filter_criteria["city"])
                
                drivers = query.all()
                recipients = [(driver.phone, driver.name) for driver in drivers]
                
            elif recipient_type == "customers":
                query = db.query(Order)
                if filter_criteria:
                    if "status" in filter_criteria:
                        query = query.filter(Order.status == filter_criteria["status"])
                    if "date_from" in filter_criteria:
                        query = query.filter(Order.created_at >= filter_criteria["date_from"])
                
                orders = query.all()
                # Get unique customer phones
                customer_phones = set()
                for order in orders:
                    customer_phones.add(order.customer_phone)
                
                recipients = [(phone, "Customer") for phone in customer_phones]
            
            # Send messages
            results = []
            for phone, name in recipients:
                personalized_message = message.replace("{name}", name)
                sms_result = self.send_sms(phone, personalized_message)
                results.append({
                    "phone": phone,
                    "name": name,
                    "result": sms_result
                })
            
            success_count = sum(1 for result in results if result["result"]["success"])
            
            return {
                "success": True,
                "message": f"Bulk notification sent to {success_count}/{len(results)} recipients",
                "results": results
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def send_delivery_summary_email(self, date: str, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send daily delivery summary email to admin"""
        try:
            subject = f"Daily Delivery Summary - {date}"
            
            html_body = f"""
            <html>
            <body>
                <h2>Daily Delivery Summary - {date}</h2>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr><td>Total Orders</td><td>{summary_data.get('total_orders', 0)}</td></tr>
                    <tr><td>Delivered Orders</td><td>{summary_data.get('delivered_orders', 0)}</td></tr>
                    <tr><td>Pending Orders</td><td>{summary_data.get('pending_orders', 0)}</td></tr>
                    <tr><td>Cancelled Orders</td><td>{summary_data.get('cancelled_orders', 0)}</td></tr>
                    <tr><td>Active Drivers</td><td>{summary_data.get('active_drivers', 0)}</td></tr>
                    <tr><td>Delivery Rate</td><td>{summary_data.get('delivery_rate', 0)}%</td></tr>
                </table>
                
                <h3>Top Performing Drivers</h3>
                <ul>
                    {' '.join([f"<li>{driver['name']}: {driver['deliveries']} deliveries</li>" 
                             for driver in summary_data.get('top_drivers', [])])}
                </ul>
                
                <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """
            
            text_body = f"""
            Daily Delivery Summary - {date}
            
            Total Orders: {summary_data.get('total_orders', 0)}
            Delivered Orders: {summary_data.get('delivered_orders', 0)}
            Pending Orders: {summary_data.get('pending_orders', 0)}
            Cancelled Orders: {summary_data.get('cancelled_orders', 0)}
            Active Drivers: {summary_data.get('active_drivers', 0)}
            Delivery Rate: {summary_data.get('delivery_rate', 0)}%
            
            Top Performing Drivers:
            {chr(10).join([f"- {driver['name']}: {driver['deliveries']} deliveries" 
                          for driver in summary_data.get('top_drivers', [])])}
            
            Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            # Send to admin email
            admin_email = os.getenv("ADMIN_EMAIL", "admin@silodispatch.com")
            
            return self.send_email(admin_email, subject, text_body, html_body)
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_payment_reminder(self, order_id: str) -> Dict[str, Any]:
        """Send payment reminder to customer"""
        db = SessionLocal()
        
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {"success": False, "error": "Order not found"}
            
            if order.payment_status == "paid":
                return {"success": False, "error": "Order already paid"}
            
            message = f"Payment reminder: Your order {order_id[:8]} amount ₹{order.total_amount} is pending. Please complete payment to avoid delivery delays."
            
            # Send SMS reminder
            sms_result = self.send_sms(order.customer_phone, message)
            
            return {
                "success": True,
                "message": "Payment reminder sent",
                "sms_result": sms_result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    def send_driver_performance_report(self, driver_id: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send performance report to driver"""
        db = SessionLocal()
        
        try:
            driver = db.query(Driver).filter(Driver.id == driver_id).first()
            if not driver:
                return {"success": False, "error": "Driver not found"}
            
            message = f"""
            Weekly Performance Report for {driver.name}:
            
            Deliveries Completed: {report_data.get('deliveries_completed', 0)}
            Average Rating: {report_data.get('average_rating', 0):.1f}/5
            On-time Delivery Rate: {report_data.get('on_time_rate', 0)}%
            Earnings: ₹{report_data.get('earnings', 0)}
            
            Keep up the good work!
            """
            
            # Send SMS report
            sms_result = self.send_sms(driver.phone, message)
            
            return {
                "success": True,
                "message": "Performance report sent",
                "sms_result": sms_result
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            db.close()
            

# Usage example and testing
if __name__ == "__main__":
    # Initialize notification service
    notification_service = NotificationService()
    
    # Example: Send OTP
    # result = notification_service.generate_and_send_otp("order123", "+919999999999")
    # print(result)
    
    # Example: Send delivery notification
    # result = notification_service.send_delivery_notification("order123", "out_for_delivery")
    # print(result)
    
    # Example: Send bulk notification to drivers
    # result = notification_service.send_bulk_notification(
    #     "drivers", 
    #     "Hello {name}, please check your app for new assignments.",
    #     {"status": "active"}
    # )
    # print(result)
    
    print("Notification Service initialized successfully!")