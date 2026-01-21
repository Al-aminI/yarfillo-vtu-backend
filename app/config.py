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
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:h2nc6h4co2h@localhost:5432/yarfillo_vtu_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis-12972.c85.us-east-1-2.ec2.cloud.redislabs.com:12972/0")
    CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://redis-12972.c85.us-east-1-2.ec2.cloud.redislabs.com:12972/0")
    CELERY_RESULT_BACKEND = os.getenv("REDIS_URL", "redis://redis-12972.c85.us-east-1-2.ec2.cloud.redislabs.com:12972/0")
    
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
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "redis://redis-12972.c85.us-east-1-2.ec2.cloud.redislabs.com:12972/0")
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

