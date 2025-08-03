# ALX Backend GraphQL CRM

A comprehensive CRM system built with Django and GraphQL. This project provides a robust API for managing customers, products, and orders, featuring advanced capabilities like bulk operations and powerful filtering.

## Features

- **GraphQL API:** Modern, flexible API allowing clients to request exactly the data they need.
- **Customer Management:** Create, bulk-create, and filter customer records.
- **Product Management:** Manage product information, including price and stock levels.
- **Order Management:** Create orders with multiple products, with automatic calculation of the total amount.
- **Advanced Filtering:** Powerful filtering capabilities on all major models, including filtering by text, ranges, and related fields.
- **Interactive API Documentation:** Built-in GraphiQL interface for easy exploration and testing of the API.

## Technologies Used

- **Backend:** Django 5+
- **API:** GraphQL with `graphene-django`
- **Filtering:** `django-filter`
- **Database:** SQLite (for development)
- **Environment:** Python 3.12+

## Setup and Installation

Follow these steps to get the project running locally:

**1. Clone the Repository**

```bash
git clone https://github.com/your-username/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm
```

**2. Create and Activate a Virtual Environment**

```bash
# For Linux/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\\venv\\Scripts\\activate
```

**3. Install Dependencies**

Install all required packages from `requirements.txt` (or install them manually if a `requirements.txt` is not present).

```bash
pip install Django graphene-django django-filter
```

**4. Install Additional Packages for Scheduled Tasks**

Install packages required for cron jobs and background task processing:

```bash
pip install django-crontab gql[all] celery redis django-celery-beat
```

**5. Apply Database Migrations**

Create the necessary database tables based on the Django models.

```bash
python manage.py migrate
```

**6. Seed the Database (Optional)**

Populate the database with initial sample data for testing.

```bash
python seed_db.py
```

**7. Run the Development Server**

Start the Django development server.

```bash
python manage.py runserver
```

## Scheduled Tasks and Background Processing

This CRM system implements comprehensive task scheduling using both cron jobs and Celery for different types of automated operations.

### Task 0: Customer Cleanup Script (Shell Script + Cron)

**Purpose:** Automatically remove inactive customers (no orders in the last year) to maintain database efficiency.

**File:** `crm/cron_jobs/clean_inactive_customers.sh`
**Schedule:** Weekly (Sundays at 2:00 AM)

```bash
# Manual execution
./crm/cron_jobs/clean_inactive_customers.sh

# Install cron job
crontab -e
# Add: 0 2 * * 0 /home/meyvn/Desktop/ProDev-Backend/alx-backend-graphql_crm/crm/cron_jobs/clean_inactive_customers.sh >/dev/null 2>&1
```

**Logs:** `/tmp/customer_cleanup_log.txt`

### Task 1: GraphQL Order Reminders (Python Script + Cron)

**Purpose:** Send order reminders by querying recent orders through GraphQL and logging reminder actions.

**File:** `crm/cron_jobs/send_order_reminders.py`
**Schedule:** Daily (8:00 AM)

```bash
# Manual execution
python crm/cron_jobs/send_order_reminders.py

# Install cron job
crontab -e
# Add: 0 8 * * * cd /home/meyvn/Desktop/ProDev-Backend/alx-backend-graphql_crm && source venv/bin/activate && python crm/cron_jobs/send_order_reminders.py >/dev/null 2>&1
```

**Logs:** `/tmp/order_reminders_log.txt`

### Task 2: Heartbeat Logger (django-crontab)

**Purpose:** Regular system health checks and low stock monitoring using Django's cron integration.

**File:** `crm/cron.py`
**Functions:**

- `log_crm_heartbeat()`: Every 5 minutes - logs system heartbeat via GraphQL hello query
- `update_low_stock()`: Every 12 hours - triggers low stock product updates

```bash
# Install django-crontab jobs
python manage.py crontab add

# View installed jobs
python manage.py crontab show

# Remove jobs
python manage.py crontab remove
```

**Configuration in `settings.py`:**

```python
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]
```

**Logs:** `/tmp/crm_heartbeat_log.txt`

### Task 3: GraphQL Stock Alert Mutation

**Purpose:** Batch update low stock products through GraphQL mutations for inventory management.

**Implementation:** `crm/schema.py` - `UpdateLowStockProducts` mutation
**Integration:** Called automatically by `update_low_stock()` cron function

```graphql
mutation {
  updateLowStockProducts(threshold: 10) {
    success
    message
    updatedProducts {
      id
      name
      stock
    }
  }
}
```

### Task 4: Celery Background Tasks

**Purpose:** Asynchronous generation of CRM reports and background task processing using Redis as message broker.

**Files:**

- `crm/celery.py`: Celery configuration with periodic task scheduling
- `crm/tasks.py`: Background task definitions

**Setup Redis and Start Celery:**

```bash
# Install and start Redis
sudo apt install redis-server
redis-server

# Start Celery worker
celery -A crm worker -l info --detach

# Start Celery Beat for periodic tasks
celery -A crm beat -l info --detach
```

**Available Tasks:**

- `generate_crm_report()`: Weekly CRM reports (Sundays)
- `test_celery_task()`: System heartbeat every 30 minutes

**Manual Task Execution:**

```python
from crm.tasks import generate_crm_report, test_celery_task

# Asynchronous execution
result = generate_crm_report.delay()
test_result = test_celery_task.delay("Custom message")

# Check task status
print(result.state)
print(result.result)
```

**Logs:** `/tmp/crm_report_log.txt`, `/tmp/celery_test_log.txt`

**Periodic Task Configuration:**

- Weekly CRM reports: Every 7 days
- Celery heartbeat tests: Every 30 minutes

### System Requirements

**For Cron Jobs:**

- System cron daemon running
- Virtual environment properly configured
- Django server accessible at localhost:8000

**For Celery:**

- Redis server running on localhost:6379
- Celery and django-celery-beat packages installed
- Proper CELERY configuration in Django settings

### Monitoring and Logs

All scheduled tasks write to dedicated log files in `/tmp/`:

- `customer_cleanup_log.txt`: Customer cleanup operations
- `order_reminders_log.txt`: Order reminder activities
- `crm_heartbeat_log.txt`: System heartbeat logs
- `crm_report_log.txt`: Celery-generated CRM reports
- `celery_test_log.txt`: Celery task execution logs

### Troubleshooting

**Cron Jobs Not Running:**

```bash
# Check cron service
sudo systemctl status cron

# View cron logs
sudo journalctl -u cron

# Test script permissions
ls -la crm/cron_jobs/
```

**Celery Issues:**

```bash
# Check Redis connection
redis-cli ping

# Check Celery worker status
celery -A crm inspect active

# View Celery logs
celery -A crm events
```

**Django-crontab Issues:**

```bash
# List installed crontab jobs
python manage.py crontab show

# Re-add jobs if missing
python manage.py crontab remove
python manage.py crontab add
```

## Usage

Once the server is running, you can access the GraphQL API at the following endpoint:

- **GraphiQL Interface:** `http://127.0.0.1:8000/graphql`

Use the GraphiQL interface to explore the schema and execute queries and mutations. See the `running.md` file for detailed examples of queries and mutations for each implemented feature.
