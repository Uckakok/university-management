from .guest import router as guest_router
from .student import router as student_router
from .admin import router as admin_router

__all__ = ["guest_router", "student_router", "admin_router"]
