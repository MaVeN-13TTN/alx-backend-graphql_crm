# ALX Backend GraphQL CRM

A comprehensive CRM system built with Django and GraphQL. This project provides a robust API for managing customers, products, and orders, featuring advanced capabilities like bulk operations and powerful filtering.

## Features

- **GraphQL API:** Modern, flexible API allowing clients to request exactly the data they need.
- **Customer Management:** Create, bulk-create, and filter customer records.
- **Product Management:** Manage product information, including price and stock levels.
- **Order Management:** Create orders with multiple products, with automatic calculation of the total amount.
- **Advanced Filtering:** Powerful filtering capabilities on all major models, including filtering by text, ranges, and related fields.
- **Interactive API Documentation:** Built-in GraphiQL interface for easy exploration and testing of the API.

## Technologies Used

- **Backend:** Django 5+
- **API:** GraphQL with `graphene-django`
- **Filtering:** `django-filter`
- **Database:** SQLite (for development)
- **Environment:** Python 3.12+

## Setup and Installation

Follow these steps to get the project running locally:

**1. Clone the Repository**

```bash
git clone https://github.com/your-username/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm
```

**2. Create and Activate a Virtual Environment**

```bash
# For Linux/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\\venv\\Scripts\\activate
```

**3. Install Dependencies**

Install all required packages from `requirements.txt` (or install them manually if a `requirements.txt` is not present).

```bash
pip install Django graphene-django django-filter
```

**4. Apply Database Migrations**

Create the necessary database tables based on the Django models.

```bash
python manage.py migrate
```

**5. Seed the Database (Optional)**

Populate the database with initial sample data for testing.

```bash
python seed_db.py
```

**6. Run the Development Server**

Start the Django development server.

```bash
python manage.py runserver
```

## Usage

Once the server is running, you can access the GraphQL API at the following endpoint:

- **GraphiQL Interface:** `http://127.0.0.1:8000/graphql`

Use the GraphiQL interface to explore the schema and execute queries and mutations. See the `running.md` file for detailed examples of queries and mutations for each implemented feature. 