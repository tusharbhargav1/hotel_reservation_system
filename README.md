# Hotel Reservation System

A web-based Hotel Reservation System built with **Python, Flask, MySQL, and SQLAlchemy**. The application supports customer room reservations and staff operations, including check-in, check-out, bill generation, and payment recording.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Application Architecture](#application-architecture)
- [Project Structure](#project-structure)
- [Database Models](#database-models)
- [Installation and Setup](#installation-and-setup)
- [Environment Configuration](#environment-configuration)
- [Run the Application](#run-the-application)
- [Staff Login](#staff-login)
- [Application Workflow](#application-workflow)
- [Security](#security)
- [Current Limitations](#current-limitations)
- [Future Improvements](#future-improvements)

## Project Overview

The Hotel Reservation System simplifies hotel room booking and day-to-day reservation management through separate customer and staff areas.

Customers can register, log in, explore hotels, check room availability, make reservations, view their booking history and bills, and cancel eligible bookings. Staff members can manage reservations, check guests in and out, generate bills, and record payments.

The project is structured with Flask Blueprints and an application factory to keep the code modular and maintainable.

## Features

### Customer
- Customer registration and login
- Browse available hotels and rooms
- Check room availability for selected dates
- Create room reservations
- View booking history
- Cancel eligible bookings
- View booking bills

### Staff
- Separate staff login
- Staff dashboard
- View and manage bookings
- Check guests in and out
- Update room occupancy status
- Generate bills during checkout
- Record payment method and payment status

### System
- MySQL relational database
- SQLAlchemy ORM
- Password hashing
- Flask-Login session management
- Role-based route protection
- Flask-WTF CSRF protection
- Shared Jinja2 base template and static assets

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| Flask | Web application framework |
| MySQL | Relational database |
| Flask-SQLAlchemy / SQLAlchemy | ORM and database operations |
| PyMySQL | MySQL database driver |
| Flask-Login | User session and authentication management |
| Flask-WTF | CSRF protection |
| Jinja2 | HTML templating |
| HTML, CSS, JavaScript | Frontend |
| python-dotenv | Load environment variables |

## Application Architecture

```text
Browser (HTML, CSS, JavaScript, Jinja2)
                    |
                    v
              Flask Routes
       (User / Staff / Room / Hotel)
                    |
                    v
          Validation & Business Logic
                    |
                    v
              SQLAlchemy ORM
                    |
                    v
                 PyMySQL
                    |
                    v
                  MySQL
```

## Project Structure

```text
hotel-reservation/
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models.py
│   ├── security.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── user_routes.py
│   │   ├── staff_routes.py
│   │   ├── room_routes.py
│   │   └── hotel_routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── images/
│   └── templates/
│       ├── base.html
│       ├── 403.html
│       ├── 404.html
│       ├── user/
│       └── staff/
├── .env                 # Local secrets; do not commit
├── .gitignore
├── config.py
├── requirements.txt
├── run.py
└── README.md
```

> The exact template files may vary as the project evolves. Keep this structure in sync with the repository.

## Database Models

The application uses the following main SQLAlchemy models:

| Model | Description |
|---|---|
| `User` | Customer account details |
| `Staff` | Staff account details and role |
| `Hotel` | Hotel information |
| `Room` | Room details, price, capacity, and status |
| `Booking` | Customer reservation, dates, guests, and status |
| `Payment` | Payment method, amount, and payment status |
| `Bill` | Room charges, tax, discount, and total |

### Main relationships

- One user can have many bookings.
- One hotel can have many rooms.
- One room can have many bookings over time.
- Each booking belongs to one user and one room.
- A booking can have one payment record and one bill record.

## Installation and Setup

### Prerequisites

Install the following before running the project:

- Python
- MySQL Server
- Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/hotel-reservation.git
cd hotel-reservation
```

Replace `YOUR-USERNAME` with your GitHub username and use the repository's actual URL.

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, follow your system's execution-policy guidance or activate the environment using your preferred terminal.

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create the MySQL database

Open MySQL Workbench or the MySQL command line and run:

```sql
CREATE DATABASE hotel_db;
```

If the database already exists, do not drop it. Use the existing database.

### 5. Configure environment variables

Create a `.env` file in the project root. See [Environment Configuration](#environment-configuration).

### 6. Ensure database tables exist

The application models define the database schema. If this is a fresh setup, make sure your project’s database initialization or migration procedure has been run before using the application. Do not delete an existing database to resolve setup errors.

## Environment Configuration

Create `.env` in the root directory:

```env
SECRET_KEY=replace_with_a_long_random_secret_key
DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost/hotel_db
SESSION_COOKIE_SECURE=False
```

Update `YOUR_MYSQL_PASSWORD` with your local MySQL password.

**Important:**
- Never commit `.env` or real credentials to GitHub.
- Use a strong, unique `SECRET_KEY`.
- `SESSION_COOKIE_SECURE=False` is intended only for local HTTP development. Enable secure cookies when deployed over HTTPS.
- URL-encode special characters in the database password if required by the connection URL.

## Run the Application

From the project root, with the virtual environment activated:

```powershell
python run.py
```

Open the local application in your browser:

- Home: http://127.0.0.1:5000/
- Customer login: http://127.0.0.1:5000/user/login
- Customer registration: http://127.0.0.1:5000/user/register
- Staff login: http://127.0.0.1:5000/staff/login

The Flask development server is intended for local development, not production deployment.

## Staff Login

A staff account must exist in the `staff` table. For local development, you can create one using the Flask application context and a hashed password.

Start Python from the project root:

```powershell
python
```

Then run:

```python
from app import create_app
from app.extensions import db
from app.models import Staff
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    existing = Staff.query.filter_by(email="admin@hotel.com").first()

    if existing is None:
        staff = Staff(
            name="Admin Staff",
            email="admin@hotel.com",
            password_hash=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(staff)
        db.session.commit()
        print("Staff account created")
    else:
        print("Staff account already exists")
```

Exit the Python shell with `exit()`, then start the app using `python run.py`.

For this local example, the credentials are:

- **Email:** `admin@hotel.com`
- **Password:** `admin123`

Change or remove this example account before deployment. Do not use these credentials in a public production environment.

## Application Workflow

```text
Customer registers / logs in
            |
            v
Browses hotels and rooms
            |
            v
Checks availability and selects dates
            |
            v
Backend validates dates and booking conflicts
            |
            v
Booking is saved in MySQL
            |
            v
Staff views the booking
            |
            v
Check-in -> Check-out
            |
            v
Bill is generated
            |
            v
Staff records payment
```

The backend checks for overlapping confirmed or checked-in bookings before accepting a reservation. Production deployments should also use appropriate database transaction and concurrency controls to handle simultaneous booking attempts safely.

## Security

Security-related measures implemented in the project include:

- Password hashing with Werkzeug
- Flask-Login session management
- Separate customer and staff authentication flows
- Custom decorators for protected customer and staff routes
- CSRF tokens for protected form submissions
- Environment variables for sensitive configuration
- Ownership checks before customers access their booking bills

Security should be reviewed and tested before deploying the application publicly.

## Current Limitations

- Payment is currently recorded in the database; there is no live payment gateway integration.
- The Flask development server is for local development only.
- Production-grade concurrent booking protection, deployment hardening, and end-to-end testing should be completed before real-world use.

## Future Improvements

- Integrate a payment gateway such as Razorpay
- Add email booking confirmations and notifications
- Add automated tests for routes and booking conflicts
- Improve concurrency handling with database transactions and locking
- Add pagination, search, and filtering for bookings
- Add production deployment configuration, logging, and monitoring
- Add reporting and analytics for hotel staff

## Author

**Tushar Bhargav**

GitHub: [tusharbhargav1](https://github.com/tusharbhargav1)

---

If you find this project useful, feel free to star the repository.
