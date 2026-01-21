#!/bin/bash

# Setup script for Yarfillo VTU Backend using UV

echo "Setting up Yarfillo VTU Backend with UV..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment and install dependencies
echo "Creating virtual environment and installing dependencies..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
# Install dependencies directly (not as editable package)
uv pip install -r requirements.txt -r requirements-dev.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

# Initialize database migrations
echo "Initializing database migrations..."
flask db init || echo "Migrations already initialized"

# Create initial migration
echo "Creating initial migration..."
flask db migrate -m "Initial migration" || echo "Migration already exists"

# Apply migrations
echo "Applying migrations..."
flask db upgrade || echo "Migrations already applied"

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Make sure PostgreSQL and Redis are running"
echo "3. Activate the virtual environment: source .venv/bin/activate"
echo "4. Run 'python run.py' to start the server"
echo "5. In another terminal, activate venv and run: 'celery -A app.tasks.celery_app worker --loglevel=info'"
