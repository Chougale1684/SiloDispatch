# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class Payment(Base):
    __tablename__ = "payments"
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    provider_data = Column(Text)


class OrderStatus(enum.Enum):
    PENDING = "pending"
    BATCHED = "batched"
    ASSIGNED = "assigned"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class BatchStatus(enum.Enum):
    CREATED = "created"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class DriverStatus(enum.Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class PaymentMethod(enum.Enum):
    UPI = "upi"
    CASH = "cash"
    PREPAID = "prepaid"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True)
    customer_name = Column(String, nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_address = Column(Text, nullable=False)
    pincode = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Order details
    items = Column(JSON)  # [{"name": "Feed Bag", "quantity": 2, "weight": 25}]
    total_weight = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    # Status and timing
    status = Column(String, default=OrderStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    delivery_slot = Column(String)  # "morning", "afternoon", "evening"
    
    # Payment
    payment_method = Column(String, default=PaymentMethod.CASH.value)
    payment_status = Column(String, default=PaymentStatus.PENDING.value)
    
    # Relationships
    batch_id = Column(String, ForeignKey("batches.id"))
    batch = relationship("Batch", back_populates="orders")
    delivery = relationship("Delivery", back_populates="order", uselist=False)

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default=BatchStatus.CREATED.value)
    
    # Constraints
    max_weight = Column(Float, default=25.0)
    max_orders = Column(Integer, default=30)
    current_weight = Column(Float, default=0.0)
    current_orders = Column(Integer, default=0)
    
    # Route optimization
    estimated_distance = Column(Float)
    estimated_time = Column(Integer)  # in minutes
    center_latitude = Column(Float)
    center_longitude = Column(Float)
    
    # Assignment
    driver_id = Column(String, ForeignKey("drivers.id"))
    driver = relationship("Driver", back_populates="batches")
    orders = relationship("Order", back_populates="batch")

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    vehicle_type = Column(String, nullable=False)  # "bike", "auto", "van"
    vehicle_number = Column(String)
    status = Column(String, default=DriverStatus.AVAILABLE.value)
    
    # Location
    current_latitude = Column(Float)
    current_longitude = Column(Float)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    batches = relationship("Batch", back_populates="driver")
    cash_ledger = relationship("CashLedger", back_populates="driver")

class Delivery(Base):
    __tablename__ = "deliveries"
    
    id = Column(String, primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    batch_id = Column(String, ForeignKey("batches.id"), nullable=False)
    driver_id = Column(String, ForeignKey("drivers.id"), nullable=False)
    
    # OTP verification
    otp = Column(String)
    otp_generated_at = Column(DateTime)
    otp_verified_at = Column(DateTime)
    
    # Delivery tracking
    started_at = Column(DateTime)
    arrived_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Payment
    payment_method = Column(String, nullable=False)
    payment_amount = Column(Float, nullable=False)
    payment_status = Column(String, default=PaymentStatus.PENDING.value)
    payment_reference = Column(String)
    
    # Relationships
    order = relationship("Order", back_populates="delivery")

class CashLedger(Base):
    __tablename__ = "cash_ledger"
    
    id = Column(String, primary_key=True)
    driver_id = Column(String, ForeignKey("drivers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # "collection", "settlement"
    reference_id = Column(String)  # order_id or settlement_id
    timestamp = Column(DateTime, default=datetime.utcnow)
    description = Column(String)
    
    # Relationships
    driver = relationship("Driver", back_populates="cash_ledger")

class Settlement(Base):
    __tablename__ = "settlements"
    
    id = Column(String, primary_key=True)
    driver_id = Column(String, ForeignKey("drivers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    settled_at = Column(DateTime, default=datetime.utcnow)
    settled_by = Column(String)  # admin user
    notes = Column(String)