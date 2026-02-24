# Import Celery app so it's loaded when Django starts.
# This ensures shared_task decorators use the correct app instance.
from .celery import app as celery_app

__all__ = ("celery_app",)
