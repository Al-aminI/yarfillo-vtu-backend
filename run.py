"""Application entry point."""
from app import create_app
from app.config import config
from app.tasks.celery_app import celery_app
import os

# Get environment
env = os.getenv("FLASK_ENV", "development")
app = create_app(config.get(env, config["default"]))

if __name__ == "__main__":
    app.run(
        host=app.config.get("HOST", "0.0.0.0"),
        port=app.config.get("PORT", 5003),
        debug=app.config.get("DEBUG", False)
    )

