"""
Django settings for CRM application.
This file includes django-crontab configuration as required for the heartbeat logger task.
"""

# Django application configuration
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "graphene_django",
    "django_filters",
    "django_crontab",
    "django_celery_beat",
    "crm",
]

# Cron jobs configuration
CRONJOBS = [
    ("*/5 * * * *", "crm.cron.logcrmheartbeat"),
    ("0 */12 * * *", "crm.cron.update_low_stock"),
]
