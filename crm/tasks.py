"""
Celery tasks for the CRM application.

This module contains background tasks that run asynchronously using Celery.
Tasks include generating periodic reports and other long-running operations.
"""

import os
import sys
import django
from datetime import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()


@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report with customer, order, and revenue statistics.

    This task:
    1. Uses GraphQL queries to fetch CRM statistics
    2. Logs the report to /tmp/crm_report_log.txt with timestamp

    Returns:
        str: Success message with report details
    """
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # GraphQL query to get CRM statistics
        query = gql(
            """
            query GetCRMStatistics {
                allCustomers {
                    id
                }
                allOrders {
                    id
                    totalAmount
                }
            }
        """
        )

        # Execute the query
        result = client.execute(query)

        # Extract statistics
        customers = result.get("allCustomers", [])
        orders = result.get("allOrders", [])

        total_customers = len(customers)
        total_orders = len(orders)

        # Calculate total revenue
        total_revenue = 0.0
        for order in orders:
            try:
                amount = float(order.get("totalAmount", 0))
                total_revenue += amount
            except (ValueError, TypeError):
                # Skip invalid amounts
                continue

        # Format the report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_message = (
            f"{timestamp} - Report: {total_customers} customers, "
            f"{total_orders} orders, ${total_revenue:.2f} revenue"
        )

        # Log the report to file
        try:
            with open("/tmp/crm_report_log.txt", "a") as log_file:
                log_file.write(report_message + "\n")
        except Exception as file_error:
            print(f"Failed to write to report log: {file_error}")

        # Return success message
        return f"CRM Report generated successfully: {report_message}"

    except Exception as e:
        error_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"{error_timestamp} - ERROR generating CRM report: {str(e)}"

        # Log error to file
        try:
            with open("/tmp/crm_report_log.txt", "a") as log_file:
                log_file.write(error_message + "\n")
        except Exception:
            pass

        # Re-raise the exception so Celery can handle it
        raise Exception(f"CRM Report generation failed: {str(e)}")


@shared_task
def test_celery_task(message="Default test message"):
    """
    Simple test task to verify Celery is working correctly.

    Args:
        message: Custom message to include in the test

    Returns:
        str: Success message with timestamp
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    test_message = f"Celery test task executed successfully at {timestamp} - {message}"

    # Log to test file
    try:
        with open("/tmp/celery_test_log.txt", "a") as log_file:
            log_file.write(test_message + "\n")
    except Exception as e:
        print(f"Failed to write test log: {e}")

    return test_message
