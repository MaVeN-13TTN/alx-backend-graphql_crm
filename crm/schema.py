import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
import re


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "stock", "created_at")


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
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    @staticmethod
    def resolve_all_customers(root, info):
        return Customer.objects.all()

    @staticmethod
    def resolve_all_products(root, info):
        return Product.objects.all()

    @staticmethod
    def resolve_all_orders(root, info):
        return Order.objects.prefetch_related("customer", "products").all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
