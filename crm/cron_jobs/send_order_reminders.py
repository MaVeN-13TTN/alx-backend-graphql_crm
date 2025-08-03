#!/usr/bin/env python3

import os
import sys
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Add the project root to the Python path
project_root = "/home/meyvn/Desktop/ProDev-Backend/alx-backend-graphql_crm"
sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()


def send_order_reminders():
    """Query GraphQL endpoint for recent orders and log reminders."""

    # Calculate date 7 days ago
    seven_days_ago = datetime.now() - timedelta(days=7)
    seven_days_ago_str = seven_days_ago.isoformat()

    # Set up GraphQL client
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # GraphQL query to get orders from the last 7 days
    query = gql(
        """
        query GetRecentOrders($orderDateGte: DateTime) {
            allOrders(orderDateGte: $orderDateGte) {
                id
                orderDate
                customer {
                    id
                    name
                    email
                }
                totalAmount
            }
        }
    """
    )

    try:
        # Execute the query
        result = client.execute(
            query, variable_values={"orderDateGte": seven_days_ago_str}
        )
        orders = result.get("allOrders", [])

        # Create timestamp for logging
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log each order
        with open("/tmp/order_reminders_log.txt", "a") as log_file:
            for order in orders:
                customer = order.get("customer", {})
                order_id = order.get("id")
                customer_email = customer.get("email", "N/A")

                log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}\n"
                log_file.write(log_entry)

        print("Order reminders processed!")

    except Exception as e:
        # Log errors
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("/tmp/order_reminders_log.txt", "a") as log_file:
            log_file.write(f"[{timestamp}] ERROR: {str(e)}\n")
        print(f"Error processing order reminders: {e}")


if __name__ == "__main__":
    send_order_reminders()
