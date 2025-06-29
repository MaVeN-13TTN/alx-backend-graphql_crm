import os
import django
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order


def seed_database():
    print("Seeding database...")

    # Clear existing data
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()

    # Create Customers
    customer1 = Customer.objects.create(
        name="John Doe", email="john.doe@example.com", phone="+11234567890"
    )
    customer2 = Customer.objects.create(
        name="Jane Smith", email="jane.smith@example.com", phone="123-456-7890"
    )

    # Create Products
    product1 = Product.objects.create(
        name="Laptop", description="A powerful laptop.", price=1200.00, stock=15
    )
    product2 = Product.objects.create(
        name="Mouse", description="A wireless mouse.", price=25.00, stock=100
    )
    product3 = Product.objects.create(
        name="Keyboard", description="A mechanical keyboard.", price=75.00, stock=50
    )

    # Create Orders
    order1 = Order.objects.create(customer=customer1, order_date=datetime.now())
    order1.products.add(product1, product2)
    order1.update_total_amount()

    order2 = Order.objects.create(customer=customer2, order_date=datetime.now())
    order2.products.add(product3)
    order2.update_total_amount()

    print("Database seeding complete.")


if __name__ == "__main__":
    seed_database()
