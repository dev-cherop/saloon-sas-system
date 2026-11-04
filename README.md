# Salon Management System

A full-stack salon management application designed to help salon businesses manage daily operations, customers, employees, appointments, payments, payroll, expenses, and business performance from one centralized platform.

The system supports multiple businesses, branch management, authentication, and permission-based access control.

## Features

### 1. Authentication and Authorization
- User registration and authentication.
- Secure login using JWT-based authentication.
- Password hashing.
- Role-based and permission-based access control.
- System-level permissions for platform administration.
- Business-specific access through business memberships.
- Protected frontend routes.

### 2. Business and Branch Management
- Create and manage businesses.
- Assign existing users as business administrators.
- Create and manage business branches.
- Update branch information.
- Activate and deactivate branches.
- Business-level data isolation.

### 3. Customer Management
- Register and manage customers.
- Search customers.
- View customer information.
- Track customer visit history.
- Monitor customer loyalty activity.

### 4. Appointment Management
- Create, update, and manage appointments.
- Calendar-based scheduling.
- Daily and weekly calendar views.
- Search and filter appointments.
- Manage appointment statuses.

### 5. Service Management
- Create and manage salon services.
- Maintain service pricing and information.

### 6. Worker Management
- Register and manage salon workers.
- Maintain worker information.
- Associate workers with salon operations.

### 7. Payments
- Record customer payments.
- Support multiple payment methods:
  - Cash
  - Mobile Money
  - Card
  - Bank Transfer
- Track payments associated with customer visits.
- View payment summaries.

### 8. Loyalty Management
- Configure customer loyalty settings.
- Track loyalty transactions.
- Manage customer loyalty activity.

### 9. Coupon Management
- Create and manage discount coupons.
- Support percentage-based discounts.
- Validate discount percentages.
- Manage coupon permissions.

### 10. Expense Management
- Record and manage business expenses.
- Associate expenses with branches.
- Validate branch ownership.
- Track business expenditure.

### 11. Payroll Management
- Manage worker payroll records.
- Create and update payroll entries.
- Manage payroll statuses.

### 12. Reports and Analytics
- Revenue and expense reporting.
- Net profit calculations.
- Date-based report filtering.
- Revenue and expense charts.
- CSV report exports.

### 13. Dashboard
- Daily business statistics.
- Monthly revenue.
- Monthly expenses.
- Net profit.
- Upcoming appointments.
- Recent payments.

## Technology Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic
- JWT Authentication
- Pytest

### Frontend
- React
- Vite
- JavaScript
- Tailwind CSS
- Axios
- React Router
- Recharts

### Development Tools
- Git and GitHub
- Visual Studio Code
- PostgreSQL
- Python virtual environments
- npm

## Project Structure

```text
saloon-sas-system/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── scripts/
│   │   ├── db.py
│   │   └── main.py
│   │
│   ├── migrations/
│   │   └── versions/
│   ├── tests/
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── features/
│   │   ├── layouts/
│   │   ├── services/
│   │   ├── context/
│   │   ├── components/
│   │   └── App.jsx
│   │
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## Installation and Setup

### Prerequisites

Install the following:

- Python 3.10+
- Node.js and npm
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/dev-cherop/saloon-sas-system.git

cd saloon-sas-system
```

### 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Database Configuration

Create a PostgreSQL database for the application.

Configure your database connection in the backend environment configuration.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/salon_db
```

Configure other required environment variables, including your JWT secret and authentication settings, according to the backend configuration.

### 4. Database Migrations

Run database migrations:

```bash
alembic upgrade head
```

This creates the database schema using the project's migration history.

### 5. Start the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Frontend Setup

Open another terminal:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Configure the frontend API URL in `.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Authorization Architecture

The application uses permission-based authorization to support flexible business roles and future system expansion.

### System-Level Permissions

System administrators can perform platform-level operations based on assigned system permissions.

Example:

```text
system:businesses:create
```

### Business-Level Permissions

Business users receive permissions through their business memberships and assigned roles.

Examples:

```text
settings:manage
reports:read
coupons:read
coupons:create
coupons:update
coupons:delete
```

Business-level operations are scoped to the relevant business to prevent unauthorized access to another business's data.

Authorization is based on explicit permissions rather than relying exclusively on hardcoded role names.

## Testing

The backend uses Pytest.

Run the complete backend test suite:

```bash
cd backend

python -m pytest -q
```

Run tests for a specific module:

```bash
python -m pytest tests/test_business.py -q
```

Frontend production build:

```bash
cd frontend

npm run build
```

## API Architecture

The backend follows a layered architecture:

- **Routes:** Handle HTTP requests and responses.
- **Schemas:** Validate incoming requests and structure responses.
- **Models:** Define database entities and relationships.
- **Services:** Contain business logic.
- **Core:** Contains authentication, authorization, and application configuration.
- **Migrations:** Manage database schema changes.

## Future Improvements

Planned areas for further development include:

- Advanced payroll processing and payslip generation.
- Payslip import and export.
- PDF and Excel report exports.
- SMS and WhatsApp notifications.
- Automated appointment reminders.
- Advanced inventory management.
- Improved financial analytics.
- Audit logs and security enhancements.
- Expanded business administration features.

## Development

This project is developed as an end-to-end full-stack application, combining Python backend development with modern React frontend development.

The architecture is designed to support maintainability, scalability, multi-business operations, and future functionality.

## Repository

GitHub:

https://github.com/dev-cherop/saloon-sas-system

## License

No open-source license has been specified yet.
