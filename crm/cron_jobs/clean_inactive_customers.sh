#!/bin/bash

# Navigate to the Django project directory
cd /home/meyvn/Desktop/ProDev-Backend/alx-backend-graphql_crm

# Activate virtual environment
source venv/bin/activate

# Execute Django shell command to delete inactive customers
DELETED_COUNT=$(python manage.py shell -c "
from crm.models import Customer, Order
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders OR customers whose most recent order is older than a year
inactive_customers = Customer.objects.filter(
    Q(orders__isnull=True) | 
    Q(orders__order_date__lt=one_year_ago)
).distinct()

# Count inactive customers
count = inactive_customers.count()

# Delete inactive customers
if count > 0:
    inactive_customers.delete()

# Print only the count
print(count)
" | tail -1)

# Create timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log the result to the specified file
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt
