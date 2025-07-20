# services/batch_processing.py
from datetime import datetime
from models.models import Batch, Order
from utils.clustering import create_optimized_batches

class BatchProcessor:
    def auto_create_batches(self, db):
        """Auto-create batches every hour"""
        pending_orders = db.query(Order).filter(Order.status == "pending").all()
        if pending_orders:
            batches = create_optimized_batches(pending_orders)
            # Save batches to DB
            # Update order statuses
            db.commit()