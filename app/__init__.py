"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, limiter
from app.api.v1 import api_bp
from app.errors.handlers import register_error_handlers


def create_app(config_class=Config):
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # CORS: allow all origins
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register API blueprint (includes Swagger documentation)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

