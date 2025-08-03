# CRM Cron Jobs

This directory contains automated scripts and cron job configurations for the ALX Backend GraphQL CRM system. These scripts handle routine maintenance tasks and automated processes to keep the CRM system running efficiently.

## Overview

The cron jobs implemented here automate critical business processes including:

- Customer data cleanup and maintenance
- Order reminder notifications
- System monitoring and logging

## Scripts

### 1. Customer Cleanup Script (`clean_inactive_customers.sh`)

**Purpose**: Automatically removes inactive customers who have no orders or haven't placed orders in the last year.

**Features**:

- Deletes customers with no orders
- Removes customers whose most recent order is older than 365 days
- Logs the number of deleted customers with timestamps
- Uses Django ORM for safe database operations

**Schedule**: Runs every Sunday at 2:00 AM

**Log Location**: `/tmp/customer_cleanup_log.txt`

**Usage**:

```bash
# Manual execution
./crm/cron_jobs/clean_inactive_customers.sh

# Add to system crontab
crontab crm/cron_jobs/customer_cleanup_crontab.txt
```

### 2. Order Reminders Script (`send_order_reminders.py`)

**Purpose**: Queries the GraphQL API to find recent orders and logs reminder information for follow-up activities.

**Features**:

- Uses GraphQL client to query orders from the last 7 days
- Connects to the Django GraphQL endpoint at `http://localhost:8000/graphql`
- Logs order IDs and customer emails for reminder processing
- Includes error handling and connection retry logic

**Schedule**: Runs daily at 8:00 AM

**Log Location**: `/tmp/order_reminders_log.txt`

**Usage**:

```bash
# Manual execution
python crm/cron_jobs/send_order_reminders.py

# Add to system crontab
crontab crm/cron_jobs/order_reminders_crontab.txt
```

## File Structure

```
crm/cron_jobs/
├── README.md                           # This documentation
├── clean_inactive_customers.sh         # Customer cleanup script
├── customer_cleanup_crontab.txt        # Cron schedule for customer cleanup
├── send_order_reminders.py            # Order reminders script
└── order_reminders_crontab.txt        # Cron schedule for order reminders
```

## Cron Schedules

| Script           | Schedule                | Cron Expression | Description                                 |
| ---------------- | ----------------------- | --------------- | ------------------------------------------- |
| Customer Cleanup | Every Sunday at 2:00 AM | `0 2 * * 0`     | Weekly maintenance during low-traffic hours |
| Order Reminders  | Daily at 8:00 AM        | `0 8 * * *`     | Daily business process during office hours  |

## Installation and Setup

### Prerequisites

1. **Virtual Environment**: Ensure the Python virtual environment is activated
2. **Django Server**: The GraphQL endpoint must be accessible at `http://localhost:8000/graphql`
3. **Dependencies**: Required Python packages (gql, django, etc.) must be installed

### Installation Steps

1. **Install Dependencies**:

   ```bash
   pip install gql[all]
   ```

2. **Set Executable Permissions**:

   ```bash
   chmod +x crm/cron_jobs/clean_inactive_customers.sh
   chmod +x crm/cron_jobs/send_order_reminders.py
   ```

3. **Test Scripts Manually**:

   ```bash
   # Test customer cleanup
   ./crm/cron_jobs/clean_inactive_customers.sh

   # Test order reminders (ensure Django server is running)
   python crm/cron_jobs/send_order_reminders.py
   ```

4. **Add to System Crontab**:
   ```bash
   # Add both cron jobs
   crontab -l > current_crontab
   cat crm/cron_jobs/customer_cleanup_crontab.txt >> current_crontab
   cat crm/cron_jobs/order_reminders_crontab.txt >> current_crontab
   crontab current_crontab
   rm current_crontab
   ```

## Log Files

### Customer Cleanup Log (`/tmp/customer_cleanup_log.txt`)

```
[2025-08-03 16:51:44] Deleted 1 inactive customers
[2025-08-03 16:52:30] Deleted 0 inactive customers
```

### Order Reminders Log (`/tmp/order_reminders_log.txt`)

```
[2025-08-03 14:01:19] Order ID: T3JkZXJUeXBlOjM=, Customer Email: john.doe@example.com
[2025-08-03 14:01:19] Order ID: T3JkZXJUeXBlOjQ=, Customer Email: jane.smith@example.com
```

## Troubleshooting

### Common Issues

1. **Python Command Not Found**:

   - Ensure virtual environment is activated
   - Use absolute paths in cron jobs

2. **GraphQL Connection Refused**:

   - Verify Django server is running on port 8000
   - Check firewall settings
   - Ensure GraphQL endpoint is accessible

3. **Permission Denied**:

   - Check file permissions: `chmod +x script_name`
   - Ensure log directories are writable

4. **Django Setup Errors**:
   - Verify `DJANGO_SETTINGS_MODULE` environment variable
   - Ensure project root is in Python path

### Debugging Commands

```bash
# Check cron jobs are installed
crontab -l

# View recent log entries
tail -f /tmp/customer_cleanup_log.txt
tail -f /tmp/order_reminders_log.txt

# Test GraphQL endpoint
curl -X POST http://localhost:8000/graphql -H "Content-Type: application/json" -d '{"query":"{ __schema { types { name } } }"}'

# Check Django server status
ps aux | grep "manage.py runserver"
```

## Monitoring and Maintenance

### Best Practices

1. **Log Rotation**: Consider implementing log rotation for long-running systems
2. **Error Alerting**: Set up monitoring for script failures
3. **Performance Monitoring**: Track execution times and resource usage
4. **Backup Strategy**: Include log files in backup procedures

### Monitoring Script Health

```bash
# Check if scripts are running successfully
grep "ERROR" /tmp/order_reminders_log.txt
grep "Deleted" /tmp/customer_cleanup_log.txt

# Monitor cron execution
grep "send_order_reminders" /var/log/syslog
grep "clean_inactive_customers" /var/log/syslog
```

## Security Considerations

- Scripts run with user-level permissions
- Log files are stored in `/tmp` (consider more secure locations for production)
- Database operations use Django ORM for safety
- GraphQL queries are parameterized to prevent injection

## Contributing

When adding new cron jobs:

1. Follow the naming convention: `script_name.{sh|py}`
2. Create corresponding `script_name_crontab.txt` file
3. Add executable permissions
4. Update this README with documentation
5. Include error handling and logging
6. Test thoroughly before deployment

## License

This code is part of the ALX Backend GraphQL CRM project.
