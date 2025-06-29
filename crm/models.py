from django.db import models
from django.utils import timezone
import re
from django.core.exceptions import ValidationError
from decimal import Decimal

# Create your models here.


class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.phone:
            if not re.match(r"^(\+1\d{10}|\d{3}-\d{3}-\d{4})$", self.phone):
                raise ValidationError({"phone": "Invalid phone number format."})

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    products = models.ManyToManyField(Product, related_name="orders")
    order_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def update_total_amount(self):
        self.total_amount = sum(product.price for product in self.products.all())
        self.save()

    def __str__(self):
        return f"Order {self.pk} by {self.customer.name}"
