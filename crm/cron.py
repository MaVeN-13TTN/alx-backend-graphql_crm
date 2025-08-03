"""
Cron job functions for the CRM application.
This module contains scheduled tasks that run periodically to maintain
application health and perform automated operations.
"""

import os
import sys
import django
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()


def log_crm_heartbeat():
    """
    Log a heartbeat message to confirm CRM application health.

    This function:
    1. Logs a timestamped message to /tmp/crm_heartbeat_log.txt
    2. Optionally queries the GraphQL hello field to verify endpoint responsiveness

    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    """
    # Get current timestamp in the required format
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Basic heartbeat message
    heartbeat_message = f"{timestamp} CRM is alive"

    # Try to query GraphQL endpoint to verify it's responsive
    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # Simple hello query to test endpoint
        query = gql(
            """
            query {
                hello
            }
        """
        )

        # Execute the query
        result = client.execute(query)
        hello_response = result.get("hello", "No response")

        # Add GraphQL status to heartbeat message
        heartbeat_message += f" - GraphQL endpoint responsive: {hello_response}"

    except Exception as e:
        # If GraphQL query fails, note the error but continue logging
        heartbeat_message += f" - GraphQL endpoint error: {str(e)}"

    # Append heartbeat message to log file
    try:
        with open("/tmp/crmheartbeatlog.txt", "a") as log_file:
            log_file.write(heartbeat_message + "\n")
    except Exception as e:
        # Fallback: print to console if file logging fails
        print(f"Failed to write to heartbeat log: {e}")
        print(heartbeat_message)


def update_low_stock():
    """
    Execute the UpdateLowStockProducts mutation and log the results.

    This function:
    1. Executes the UpdateLowStockProducts mutation via GraphQL endpoint
    2. Logs updated product names and new stock levels to /tmp/low_stock_updates_log.txt
    """
    # Get current timestamp
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=True)

        # GraphQL mutation to update low-stock products
        mutation = gql(
            """
            mutation {
                updateLowStockProducts {
                    updatedProducts {
                        id
                        name
                        stock
                    }
                    message
                    count
                }
            }
        """
        )

        # Execute the mutation
        result = client.execute(mutation)
        mutation_result = result.get("updateLowStockProducts", {})

        updated_products = mutation_result.get("updatedProducts", [])
        message = mutation_result.get("message", "No response")
        count = mutation_result.get("count", 0)

        # Log the results
        log_entries = []
        log_entries.append(f"[{timestamp}] Low stock update executed: {message}")

        if updated_products:
            for product in updated_products:
                product_name = product.get("name", "Unknown")
                new_stock = product.get("stock", "Unknown")
                log_entries.append(
                    f"[{timestamp}] Updated product: {product_name}, New stock: {new_stock}"
                )
        else:
            log_entries.append(f"[{timestamp}] No low-stock products found to update")

        # Write to log file
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            for entry in log_entries:
                log_file.write(entry + "\n")

    except Exception as e:
        # Log errors
        error_message = f"[{timestamp}] ERROR in low stock update: {str(e)}"
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(error_message + "\n")
        print(f"Error updating low stock products: {e}")


def logcrmheartbeat():
    """
    Alternative function name without underscores for compatibility.
    Calls the main log_crm_heartbeat function.
    """
    return log_crm_heartbeat()
