# ALX Backend GraphQL CRM

This project is a Customer Relationship Management (CRM) system built with Django and GraphQL.

## Task 0: Set Up GraphQL Endpoint

### Implementation Details

- **Django Project:** Set up a Django project named `alx_backend_graphql_crm` and a core application named `crm`.
- **Dependencies:** Installed `graphene-django` and `django-filter` to enable GraphQL functionality.
- **GraphQL Endpoint:** Configured the primary GraphQL endpoint at `/graphql`, with the GraphiQL interface enabled for interactive testing.
- **Initial Schema:** Created an initial schema (`alx_backend_graphql_crm/schema.py`) with a simple `hello` query to verify the endpoint setup.

### How to Test

Visit `http://localhost:8000/graphql` and run the following query to confirm the endpoint is working:

```graphql
{
  hello
}
```

**Expected Response:**

```json
{
  "data": {
    "hello": "Hello, GraphQL!"
  }
}
```

---

## Task 1: Build and Seed a CRM Database with GraphQL Integration

### Implementation Details

- **Database Models:** Defined `Customer`, `Product`, and `Order` models in `crm/models.py` to represent the core data structures.
- **Database Migrations:** Generated and applied database migrations to create the necessary tables.
- **GraphQL Schema (`crm/schema.py`):**
    - **Types:** Created `CustomerType`, `ProductType`, and `OrderType` corresponding to the Django models.
    - **Mutations:** Implemented a suite of mutations to create and manage data:
        - `createCustomer`: Creates a single customer with validation for email and phone number.
        - `bulkCreateCustomers`: Creates multiple customers in a single, atomic transaction, returning lists of successful creations and any validation errors.
        - `createProduct`: Creates a product with validation for price and stock.
        - `createOrder`: Creates an order, associates it with a customer and products, and automatically calculates the `total_amount`.
- **Database Seeding:** Created a `seed_db.py` script to populate the database with initial sample data for testing purposes.

### How to Test

Use the following mutations in the GraphiQL interface to test the functionality.

**1. Create a single customer:**

```graphql
mutation {
  createCustomer(input: {
    name: "Alice",
    email: "alice@example.com",
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
  }
}
```

**2. Bulk create customers:**

```graphql
mutation {
  bulkCreateCustomers(input: [
    { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
      email
    }
    errors
  }
}
```

**3. Create a product:**

```graphql
mutation {
  createProduct(input: {
    name: "Laptop",
    price: 999.99,
    stock: 10
  }) {
    product {
      id
      name
      price
      stock
    }
  }
}
```

**4. Create an order with products:**
*(Note: You may need to adjust `customerId` and `productIds` based on the actual IDs in your database after running the previous mutations or the seed script.)*

```graphql
mutation {
  createOrder(input: {
    customerId: "1",
    productIds: ["1"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
  }
}
```

---

## Task 3: Add Filtering and Sorting

### Implementation Details

- **Dependencies:** Added `django_filters` to the `INSTALLED_APPS` in `settings.py`.
- **GraphQL Schema (`crm/schema.py`):**
    - **Node Interface:** Updated `CustomerType`, `ProductType`, and `OrderType` to implement Graphene's `Node` interface, which is required for connections.
    - **Filtering:** Replaced `graphene.List` with `graphene_django.filter.DjangoFilterConnectionField` for `all_customers`, `all_products`, and `all_orders`.
    - **Filter Fields:** Defined the available filters directly in each type's `Meta` class using the `filter_fields` attribute. This enables filtering by text, ranges, and related fields (e.g., filtering orders by customer name).

### How to Test

Use the following queries in the GraphiQL interface to test the filtering functionality. Note that with `DjangoFilterConnectionField`, filter arguments are passed directly to the query, not inside a `filter` object.

**1. Filter customers by name (case-insensitive) and creation date:**

```graphql
query {
  allCustomers(name_Icontains: "john", createdAt_Gte: "2025-06-29T00:00:00+00:00") {
    edges {
      node {
        id
        name
        email
        createdAt
      }
    }
  }
}
```

**2. Filter products by price range:**

```graphql
query {
  allProducts(price_Gte: 100, price_Lte: 1500) {
    edges {
      node {
        id
        name
        price
        stock
      }
    }
  }
}
```

**3. Filter orders by customer name and product name:**

```graphql
query {
  allOrders(customer_Name_Icontains: "john", products_Name_Icontains:"laptop") {
    edges {
      node {
        id
        customer {
          name
        }
        products {
          name
          price
        }
        totalAmount
        orderDate
      }
    }
  }
}
``` 