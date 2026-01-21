# Yarfillo VTU Backend API

Backend API for the Yarfillo VTU Platform built with Flask, PostgreSQL, and Payscribe API integration.

## Features

- User authentication (signup, login)
- Wallet management with NGN Virtual Accounts
- Airtime purchase
- Data bundle purchase
- Transaction history
- Beneficiary management
- Webhook processing for virtual account payments

## Tech Stack

- **Flask**: Web framework
- **PostgreSQL**: Database
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations
- **Celery + Redis**: Task queue for async processing
- **JWT**: Authentication
- **Payscribe API**: VTU services integration
- **UV**: Fast Python package manager

## Setup Instructions

### Prerequisites

- Python 3.12+
- PostgreSQL 12+
- Redis 6+
- Payscribe API credentials

### Installation

1. **Install UV** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone the repository** (if not already done):
   ```bash
   cd yarfillo-vtu-backend
   ```

3. **Run setup script** (recommended):
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

   Or manually:
   ```bash
   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -r requirements.txt -r requirements-dev.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**:
   ```bash
   # Create PostgreSQL database
   createdb yarfillo_vtu_db
   
   # Initialize migrations
   flask db init
   
   # Create initial migration
   flask db migrate -m "Initial migration"
   
   # Apply migrations
   flask db upgrade
   ```

6. **Run the application**:
   ```bash
   # Activate virtual environment first
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Then run the application
   python run.py
   ```

### Running Celery Worker

In a separate terminal, run the Celery worker:

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

### Running Celery Beat (for periodic tasks)

In a separate terminal, run Celery beat:

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run Celery beat
celery -A app.tasks.celery_app beat --loglevel=info
```

## API Documentation

Interactive Swagger/OpenAPI documentation is available at:
- **Swagger UI**: `http://localhost:5000/api/v1/docs`
- **ReDoc**: `http://localhost:5000/api/v1/docs` (alternative view)

The documentation includes:
- All API endpoints with descriptions
- Request/response schemas
- Authentication requirements
- Example requests and responses
- Try-it-out functionality for testing endpoints

### Authentication in Swagger UI

To test protected endpoints in Swagger UI:
1. First, call the `/auth/login` endpoint to get a JWT token
2. Click the "Authorize" button at the top of the Swagger UI
3. Enter: `Bearer {your_token}` (replace `{your_token}` with the actual token)
4. Click "Authorize" and "Close"
5. Now you can test protected endpoints

## API Endpoints

### Authentication

- `POST /api/v1/auth/signup` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user (requires auth)

### Wallet

- `GET /api/v1/wallet/balance` - Get wallet balance
- `GET /api/v1/wallet/account-details` - Get virtual account details

### Airtime

- `POST /api/v1/airtime/purchase` - Purchase airtime

### Data

- `GET /api/v1/data/plans?network={network}` - Get data plans
- `POST /api/v1/data/purchase` - Purchase data bundle

### Transactions

- `GET /api/v1/transactions` - Get transaction history
- `GET /api/v1/transactions/{id}` - Get specific transaction

### Beneficiaries

- `GET /api/v1/beneficiaries` - Get all beneficiaries
- `POST /api/v1/beneficiaries` - Create beneficiary
- `DELETE /api/v1/beneficiaries/{id}` - Delete beneficiary

### Webhooks

- `POST /api/v1/webhooks/payscribe` - Payscribe webhook endpoint

## Environment Variables

See `.env.example` for all required environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `PAYSCRIBE_BASE_URL`: Payscribe API base URL
- `PAYSCRIBE_API_TOKEN`: Payscribe API token
- `PAYSCRIBE_SECRET_KEY`: Payscribe secret key for webhook verification
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `SECRET_KEY`: Flask secret key

## Project Structure

```
yarfillo-vtu-backend/
├── app/
│   ├── api/           # API endpoints
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   ├── integrations/  # External API clients
│   ├── tasks/        # Celery tasks
│   ├── utils/        # Utilities
│   └── errors/       # Error handling
├── migrations/       # Database migrations
├── tests/           # Tests
├── scripts/         # Setup and utility scripts
├── run.py           # Application entry point
├── pyproject.toml   # Project configuration (UV)
└── requirements.txt # Legacy requirements (use pyproject.toml)
```

## Development

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run tests
pytest
```

### Code Formatting

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Format code
black .
isort .
```

### Adding Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Add a new dependency
uv pip install package-name

# Add a dev dependency
uv pip install package-name --dev

# Note: Manually update pyproject.toml with the new dependency
```

## License

MIT

