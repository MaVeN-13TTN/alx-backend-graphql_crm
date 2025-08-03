"""
GraphQL schema for the CRM application.

Note: Pylance warnings about "No parameter named" in GraphQL mutations are expected.
GraphQL mutations use dynamic parameter binding that Pylance cannot analyze statically.
"""

# pylint: disable=no-member,unused-argument
# type: ignore

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
import re


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "name": ["icontains"],
            "email": ["icontains"],
            "created_at": ["gte", "lte"],
        }


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "stock", "created_at")
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "name": ["icontains"],
            "price": ["gte", "lte"],
            "stock": ["exact", "gte", "lte"],
        }


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "products",
            "order_date",
            "total_amount",
            "created_at",
        )
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            "customer__name": ["icontains"],
            "products__name": ["icontains"],
            "products__id": ["exact"],
            "total_amount": ["gte", "lte"],
            "order_date": ["gte", "lte"],
        }


class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, input):
        try:
            if Customer.objects.filter(email=input.email).exists():
                raise ValidationError("Email already exists.")

            if input.phone and not re.match(
                r"^(\+1\d{10}|\d{3}-\d{3}-\d{4})$", input.phone
            ):
                raise ValidationError("Invalid phone number format.")

            customer = Customer(
                name=input.name, email=input.email, phone=input.get("phone", "")
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(
                customer=customer, message="Customer created successfully."
            )
        except ValidationError as e:
            raise Exception(str(e))


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CreateCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        successful_customers = []
        error_messages = []

        with transaction.atomic():
            for i, customer_data in enumerate(input):
                try:
                    if Customer.objects.filter(email=customer_data.email).exists():
                        raise ValidationError(
                            f"Record {i+1}: Email '{customer_data.email}' already exists."
                        )

                    if customer_data.phone and not re.match(
                        r"^(\+1\d{10}|\d{3}-\d{3}-\d{4})$", customer_data.phone
                    ):
                        raise ValidationError(
                            f"Record {i+1}: Invalid phone number format for '{customer_data.phone}'."
                        )

                    customer = Customer(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.get("phone", ""),
                    )
                    customer.full_clean()
                    customer.save()
                    successful_customers.append(customer)
                except ValidationError as e:
                    error_messages.append(f"Record {i+1}: {e}")
                except Exception as e:
                    error_messages.append(
                        f"Record {i+1}: An unexpected error occurred: {e}"
                    )

        return BulkCreateCustomers(
            customers=successful_customers, errors=error_messages
        )


class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)

    @staticmethod
    def mutate(root, info, input):
        try:
            if input.price <= 0:
                raise ValidationError("Price must be positive.")
            if input.stock and input.stock < 0:
                raise ValidationError("Stock cannot be negative.")

            product = Product(
                name=input.name, price=input.price, stock=input.get("stock", 0)
            )
            product.full_clean()
            product.save()
            return CreateProduct(product=product)
        except ValidationError as e:
            raise Exception(str(e))


class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)

    @staticmethod
    def mutate(root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)

            if not input.product_ids:
                raise ValidationError("At least one product must be selected.")

            products = Product.objects.filter(pk__in=input.product_ids)
            if len(products) != len(input.product_ids):
                raise ValidationError("Invalid product ID found.")

            with transaction.atomic():
                order = Order(customer=customer)
                if input.order_date:
                    order.order_date = input.order_date
                order.save()
                order.products.set(products)
                order.update_total_amount()

            return CreateOrder(order=order)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID.")
        except ValidationError as e:
            raise Exception(str(e))


class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = graphene.List(
        CustomerType,
        name=graphene.String(),
        email=graphene.String(),
        created_at_gte=graphene.DateTime(),
        created_at_lte=graphene.DateTime(),
        phone_pattern=graphene.String(),
        order_by=graphene.String(),
    )
    all_products = graphene.List(
        ProductType,
        name=graphene.String(),
        price_gte=graphene.Decimal(),
        price_lte=graphene.Decimal(),
        stock_gte=graphene.Int(),
        stock_lte=graphene.Int(),
        low_stock=graphene.Boolean(),
        order_by=graphene.String(),
    )
    all_orders = graphene.List(
        OrderType,
        customer_name=graphene.String(),
        product_name=graphene.String(),
        product_id=graphene.ID(),
        total_amount_gte=graphene.Decimal(),
        total_amount_lte=graphene.Decimal(),
        order_date_gte=graphene.DateTime(),
        order_date_lte=graphene.DateTime(),
        order_by=graphene.String(),
    )

    def resolve_hello(self, info):
        return "Hello from CRM GraphQL API!"

    # GraphQL resolvers: 'root' parameter is intentional for GraphQL context
    def resolve_all_customers(root, info, **kwargs):  # type: ignore[misc]
        filters = {
            "name__icontains": kwargs.get("name"),
            "email__icontains": kwargs.get("email"),
            "created_at__gte": kwargs.get("created_at_gte"),
            "created_at__lte": kwargs.get("created_at_lte"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        queryset = Customer.objects.filter(**filters)

        if "phone_pattern" in kwargs:
            queryset = queryset.filter(phone__startswith=kwargs["phone_pattern"])

        if "order_by" in kwargs:
            queryset = queryset.order_by(kwargs["order_by"])

        return queryset

    def resolve_all_products(root, info, **kwargs):  # type: ignore[misc]
        filters = {
            "name__icontains": kwargs.get("name"),
            "price__gte": kwargs.get("price_gte"),
            "price__lte": kwargs.get("price_lte"),
            "stock__gte": kwargs.get("stock_gte"),
            "stock__lte": kwargs.get("stock_lte"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        queryset = Product.objects.filter(**filters)

        if kwargs.get("low_stock"):
            queryset = queryset.filter(stock__lt=10)

        if "order_by" in kwargs:
            queryset = queryset.order_by(kwargs["order_by"])

        return queryset

    def resolve_all_orders(root, info, **kwargs):  # type: ignore[misc]
        filters = {
            "customer__name__icontains": kwargs.get("customer_name"),
            "products__name__icontains": kwargs.get("product_name"),
            "products__id": kwargs.get("product_id"),
            "total_amount__gte": kwargs.get("total_amount_gte"),
            "total_amount__lte": kwargs.get("total_amount_lte"),
            "order_date__gte": kwargs.get("order_date_gte"),
            "order_date__lte": kwargs.get("order_date_lte"),
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        queryset = Order.objects.filter(**filters).distinct()

        if "order_by" in kwargs:
            queryset = queryset.order_by(kwargs["order_by"])

        return queryset


class UpdateLowStockProducts(graphene.Mutation):
    """
    Mutation to update low-stock products by incrementing their stock by 10.
    Targets products with stock < 10.
    """

    class Arguments:
        pass  # No arguments needed for this mutation

    updated_products = graphene.List(ProductType)
    message = graphene.String()
    count = graphene.Int()

    @staticmethod
    def mutate(root, info):
        try:
            # Find products with low stock (< 10)
            low_stock_products = Product.objects.filter(stock__lt=10)

            updated_products = []

            with transaction.atomic():
                for product in low_stock_products:
                    # Increment stock by 10
                    product.stock += 10
                    product.save()
                    updated_products.append(product)

            count = len(updated_products)
            message = f"Successfully updated {count} low-stock products"

            # GraphQL mutation return: Pylance warnings about parameters are expected
            return UpdateLowStockProducts(  # type: ignore[call-arg]
                updated_products=updated_products, message=message, count=count
            )

        except Exception as e:
            raise Exception(f"Failed to update low-stock products: {str(e)}")


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()
