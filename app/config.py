"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_hBaQs0xbRI6v@ep-weathered-sun-ais2jvil-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"

    # Payscribe
    PAYSCRIBE_BASE_URL = os.getenv("PAYSCRIBE_BASE_URL", "https://sandbox.payscribe.ng/api/v1")
    PAYSCRIBE_API_TOKEN = os.getenv("PAYSCRIBE_API_TOKEN", "ps_pk_test_5fJUELCWRxbYyqE0mylVlfeekNK9iY0990")
    PAYSCRIBE_SECRET_KEY = os.getenv("PAYSCRIBE_SECRET_KEY", "")
    PAYSCRIBE_WEBHOOK_IPS = os.getenv("PAYSCRIBE_WEBHOOK_IP", "162.254.34.78").split(",")
    
    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "86400"))
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8080,http://localhost:5173")
    
    # Rate Limiting (in-memory when no storage URL)
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"

    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5003"))


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:h2nc6h4co2h@localhost:5432/yarfillo_vtu_test"
    WTF_CSRF_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}

