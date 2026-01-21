# UV Quick Reference Guide

This project uses [UV](https://github.com/astral-sh/uv) for fast Python package management.

## Installation

### Install UV

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or using pip:**
```bash
pip install uv
```

## Common Commands

### Setup Project

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install all dependencies (including dev)
uv pip install -r requirements.txt -r requirements-dev.txt

# Install only production dependencies
uv pip install -r requirements.txt
```

### Running Commands

```bash
# Activate virtual environment first (recommended)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Then run Python script
python run.py

# Note: uv run requires a lock file. For this project, use activated venv instead.
```

### Managing Dependencies

```bash
# Add a new dependency
uv pip install package-name

# Add a dev dependency
uv pip install package-name --dev

# Remove a dependency
uv pip uninstall package-name

# Update all dependencies
uv pip install --upgrade -e ".[dev]"

# List installed packages
uv pip list

# Show package info
uv pip show package-name
```

### Sync Dependencies

```bash
# Sync dependencies from pyproject.toml
uv pip sync pyproject.toml

# Compile dependencies (generate lock file)
uv pip compile pyproject.toml
```

### Development Workflow

```bash
# Run tests
uv run pytest

# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy app/

# Run Flask commands
uv run flask db upgrade
uv run flask db migrate -m "Description"

# Run Celery
uv run celery -A app.tasks.celery_app worker --loglevel=info
```

## Benefits of UV

- **Fast**: 10-100x faster than pip
- **Reliable**: Better dependency resolution
- **Modern**: Uses pyproject.toml standard
- **Compatible**: Works with existing pip workflows
- **Cross-platform**: Works on macOS, Linux, and Windows

## Migration from pip

The project still includes `requirements.txt` for compatibility, but all dependencies are now managed in `pyproject.toml`. You can use either:

- **UV (recommended)**: `uv pip install -e ".[dev]"`
- **pip (legacy)**: `pip install -r requirements.txt`

## Virtual Environment

UV creates a `.venv` directory (not `venv`). This is automatically ignored by git.

To activate:
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate      # Windows
```

## Troubleshooting

### Clear cache
```bash
uv cache clean
```

### Recreate virtual environment
```bash
rm -rf .venv
uv venv
uv pip install -e ".[dev]"
```

### Check UV version
```bash
uv --version
```

