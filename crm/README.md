# CRM Celery Setup and Documentation

This document provides comprehensive instructions for setting up and running Celery with Redis for asynchronous task processing in the ALX Backend GraphQL CRM system.

## Overview

Celery is used for:

- **Weekly CRM Reports**: Automated generation of customer, order, and revenue statistics
- **Background Tasks**: Long-running operations that don't block the web interface
- **Scheduled Jobs**: Periodic tasks using Celery Beat scheduler

## Prerequisites

### System Requirements

- Python 3.8+
- Redis server
- Django application running
- GraphQL endpoint accessible at `http://localhost:8000/graphql`

### Redis Installation

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS (using Homebrew)

```bash
brew install redis
brew services start redis
```

#### Windows

Download and install Redis from the official Redis website or use Docker:

```bash
docker run -d -p 6379:6379 redis:alpine
```

### Verify Redis Installation

```bash
redis-cli ping
# Should return: PONG
```

## Installation Steps

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install Python packages
pip install celery django-celery-beat redis

# Or install from requirements.txt
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
python manage.py migrate
```

This creates the necessary database tables for django-celery-beat to store periodic task schedules.

### 3. Verify Configuration

Check that the following are configured in `alx_backend_graphql_crm/settings.py`:

```python
# Celery configuration
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# Celery Beat schedule
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

## Running Celery

### Method 1: Development Setup (Multiple Terminals)

**Terminal 1: Django Development Server**

```bash
cd /path/to/alx-backend-graphql_crm
source venv/bin/activate
python manage.py runserver 8000
```

**Terminal 2: Celery Worker**

```bash
cd /path/to/alx-backend-graphql_crm
source venv/bin/activate
celery -A crm worker -l info
```

**Terminal 3: Celery Beat Scheduler**

```bash
cd /path/to/alx-backend-graphql_crm
source venv/bin/activate
celery -A crm beat -l info
```

**Terminal 4: Redis Server** (if not running as service)

```bash
redis-server
```

### Method 2: Production Setup (Process Manager)

Use a process manager like supervisor or systemd to manage all services.

#### Supervisor Configuration Example

Create `/etc/supervisor/conf.d/crm_celery.conf`:

```ini
[program:crm_celery_worker]
command=/path/to/venv/bin/celery -A crm worker -l info
directory=/path/to/alx-backend-graphql_crm
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:crm_celery_beat]
command=/path/to/venv/bin/celery -A crm beat -l info
directory=/path/to/alx-backend-graphql_crm
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

## Testing the Setup

### 1. Test Celery Worker

```bash
# From Django shell
python manage.py shell

# In the shell:
from crm.tasks import test_celery_task
result = test_celery_task.delay()
print(result.get())
```

### 2. Test CRM Report Generation

```bash
# From Django shell
python manage.py shell

# In the shell:
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.get())
```

### 3. Manual Report Generation

```bash
# Direct task execution (synchronous)
python manage.py shell -c "from crm.tasks import generate_crm_report; generate_crm_report()"
```

## Monitoring and Logs

### Log Files

- **CRM Reports**: `/tmp/crm_report_log.txt`
- **Test Tasks**: `/tmp/celery_test_log.txt`
- **Celery Worker**: Console output or supervisor logs
- **Celery Beat**: Console output or supervisor logs

### Check Report Logs

```bash
# View latest CRM reports
tail -f /tmp/crm_report_log.txt

# View all reports
cat /tmp/crm_report_log.txt
```

### Expected Log Format

```
2025-08-03 18:00:00 - Report: 15 customers, 42 orders, $12750.50 revenue
2025-08-10 18:00:00 - Report: 18 customers, 47 orders, $15230.75 revenue
```

## Scheduled Tasks

### Current Schedule

- **CRM Report Generation**: Every Monday at 6:00 AM UTC

### Modify Schedule

Edit `CELERY_BEAT_SCHEDULE` in `settings.py`:

```python
# Examples of different schedules
CELERY_BEAT_SCHEDULE = {
    'daily-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
    },
    'hourly-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

## Troubleshooting

### Common Issues

#### 1. Redis Connection Error

**Error**: `celery.exceptions.Retry: Connection to Redis failed`

**Solutions**:

- Verify Redis is running: `redis-cli ping`
- Check Redis URL in settings: `CELERY_BROKER_URL`
- Ensure Redis is accessible on port 6379

#### 2. Task Not Found Error

**Error**: `KeyError: 'crm.tasks.generate_crm_report'`

**Solutions**:

- Restart Celery worker after adding new tasks
- Verify task is decorated with `@shared_task`
- Check import paths in worker startup logs

#### 3. GraphQL Connection Error

**Error**: Connection refused to GraphQL endpoint

**Solutions**:

- Ensure Django server is running on port 8000
- Verify GraphQL endpoint: `curl http://localhost:8000/graphql`
- Check firewall settings

#### 4. Permission Errors

**Error**: Cannot write to `/tmp/crm_report_log.txt`

**Solutions**:

- Check file permissions: `ls -la /tmp/crm_report_log.txt`
- Create directory if needed: `mkdir -p /tmp && touch /tmp/crm_report_log.txt`
- Run with appropriate user permissions

### Debug Commands

```bash
# Check Celery configuration
celery -A crm inspect conf

# List active tasks
celery -A crm inspect active

# Check worker statistics
celery -A crm inspect stats

# Purge all pending tasks
celery -A crm purge
```

## Production Considerations

### Security

- Use Redis authentication in production
- Configure Redis to bind only to localhost
- Use SSL/TLS for Redis connections
- Set appropriate file permissions for log files

### Performance

- Monitor Redis memory usage
- Configure Celery worker concurrency based on system resources
- Set up log rotation for large log files
- Use Redis clustering for high availability

### Monitoring

- Set up monitoring for Celery worker health
- Monitor Redis server status
- Set up alerts for task failures
- Track task execution times and success rates

## Integration with Other Components

### GraphQL Schema

The CRM report task integrates with the existing GraphQL schema to fetch:

- Customer data via `allCustomers` query
- Order data via `allOrders` query
- Revenue calculations from order `totalAmount` fields

### Django-Crontab Integration

Celery tasks complement the existing django-crontab jobs:

- **django-crontab**: Simple scheduled scripts (heartbeat, stock updates)
- **Celery**: Complex background tasks with better error handling and monitoring

## API Reference

### Available Tasks

#### `generate_crm_report()`

Generates a comprehensive CRM report with customer, order, and revenue statistics.

**Returns**: Success message with report details
**Schedule**: Weekly (Mondays at 6 AM UTC)
**Log File**: `/tmp/crm_report_log.txt`

#### `test_celery_task()`

Simple test task to verify Celery is working correctly.

**Returns**: Success message with timestamp
**Log File**: `/tmp/celery_test_log.txt`

### Schedule Configuration Reference

```python
from celery.schedules import crontab

# Every minute
crontab()

# Every hour at minute 0
crontab(minute=0)

# Every day at 6:00 AM
crontab(hour=6, minute=0)

# Every Monday at 6:00 AM
crontab(day_of_week='mon', hour=6, minute=0)

# Every 1st day of month at 7:30 AM
crontab(day_of_month=1, hour=7, minute=30)
```

## Support and Maintenance

For issues or questions regarding the Celery setup:

1. Check the troubleshooting section above
2. Review Celery worker and beat logs
3. Verify Redis server status
4. Test GraphQL endpoint connectivity

This documentation is part of the ALX Backend GraphQL CRM project.
