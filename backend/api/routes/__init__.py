# Initialize the API routes package
from .core import router as core_router
from .orders import router as orders_router
from .batches import router as batches_router
from .drivers import router as drivers_router

__all__ = ["core_router", "orders_router", "batches_router", "drivers_router"]