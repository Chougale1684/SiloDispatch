# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:silofortune@localhost/silofortune_db")

# Create engine
engine = create_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    from models.models import Base
    Base.metadata.create_all(bind=engine)

# Sample data for testing
def seed_database():
    from models.models import Driver, Order
    from sqlalchemy.orm import Session
    import uuid
    
    db = SessionLocal()
    
    # Create sample drivers
    drivers = [
        Driver(
            id=str(uuid.uuid4()),
            name="Mahesh Kumar",
            phone="9876543210",
            vehicle_type="bike",
            vehicle_number="KA-03-AB-1234"
        ),
        Driver(
            id=str(uuid.uuid4()),
            name="Ravi Sharma",
            phone="9876543211",
            vehicle_type="auto",
            vehicle_number="KA-03-CD-5678"
        ),
        Driver(
            id=str(uuid.uuid4()),
            name="Suresh Gowda",
            phone="9876543212",
            vehicle_type="van",
            vehicle_number="KA-03-EF-9012"
        )
    ]
    
    for driver in drivers:
        db.add(driver)
    
    # Create sample orders
    sample_orders = [
        {
            "customer_name": "Dairy Farm A",
            "customer_phone": "9123456789",
            "customer_address": "123 Farm Road, Ramanagara",
            "pincode": "562159",
            "latitude": 12.7209,
            "longitude": 77.2833,
            "items": [{"name": "Cattle Feed", "quantity": 2, "weight": 25}],
            "total_weight": 50.0,
            "total_amount": 1200.0
        },
        {
            "customer_name": "Dairy Farm B",
            "customer_phone": "9123456790",
            "customer_address": "456 Village Center, Mandya",
            "pincode": "571401",
            "latitude": 12.5214,
            "longitude": 76.8956,
            "items": [{"name": "Cattle Feed", "quantity": 1, "weight": 25}],
            "total_weight": 25.0,
            "total_amount": 600.0
        },
        {
            "customer_name": "Dairy Farm C",
            "customer_phone": "9123456791",
            "customer_address": "789 Rural Road, Mysore",
            "pincode": "570001",
            "latitude": 12.2958,
            "longitude": 76.6394,
            "items": [{"name": "Cattle Feed", "quantity": 3, "weight": 25}],
            "total_weight": 75.0,
            "total_amount": 1800.0
        }
    ]
    
    for order_data in sample_orders:
        order = Order(
            id=str(uuid.uuid4()),
            **order_data
        )
        db.add(order)
    
    db.commit()
    db.close()
    print("Database seeded successfully!")

if __name__ == "__main__":
    create_tables()
    seed_database()