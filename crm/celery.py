"""
Celery configuration for the CRM application.

This module sets up Celery for background task processing using Redis as the message broker.
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")

# Create the Celery app
app = Celery("crm")

# Load configuration from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Configure periodic tasks using Celery Beat
app.conf.beat_schedule = {
    "generate-weekly-crm-report": {
        "task": "crm.tasks.generate_crm_report",
        "schedule": 60.0 * 60.0 * 24.0 * 7.0,  # Weekly (7 days in seconds)
        "options": {
            "expires": 60.0 * 60.0 * 6.0
        },  # Expire after 6 hours if not executed
    },
    "test-celery-heartbeat": {
        "task": "crm.tasks.test_celery_task",
        "schedule": 60.0 * 30.0,  # Every 30 minutes
        "args": ("Periodic heartbeat test",),
        "options": {"expires": 60.0 * 25.0},  # Expire after 25 minutes if not executed
    },
}

# Set timezone for beat schedule
app.conf.update(timezone="UTC")


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration"""
    print(f"Request: {self.request!r}")
    return f"Debug task executed successfully!"
