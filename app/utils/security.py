"""Security utilities for authentication and webhooks."""
import jwt
import bcrypt
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from typing import Dict, Any, Optional


def generate_token(user_id: str, expires_in: int = 86400) -> str:
    """Generate JWT token."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow()
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256"
    )


def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token."""
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def hash_pin(pin: str) -> str:
    """Hash PIN using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pin.encode("utf-8"), salt).decode("utf-8")


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Verify PIN against hash."""
    try:
        return bcrypt.checkpw(pin.encode("utf-8"), pin_hash.encode("utf-8"))
    except Exception:
        return False


def verify_webhook_ip(client_ip: str) -> bool:
    """Verify webhook request is from Payscribe server."""
    allowed_ips = current_app.config.get("PAYSCRIBE_WEBHOOK_IPS", ["162.254.34.78"])
    return client_ip in allowed_ips


def verify_webhook_hash(
    secret_key: str,
    sender_account: str,
    virtual_account: str,
    bank_code: str,
    amount: str,
    trans_id: str,
    received_hash: str
) -> bool:
    """Verify Payscribe webhook transaction hash."""
    hash_combination = f"{secret_key}{sender_account}{virtual_account}{bank_code}{amount}{trans_id}"
    computed_hash = hashlib.sha512(hash_combination.encode()).hexdigest().upper()
    return computed_hash == received_hash.upper()


def token_required(f):
    """Decorator for protected routes."""
    @wraps(f)
    def decorated(self, *args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]  # Bearer {token}
            except IndexError:
                return {"status": False, "message": "Invalid token format"}, 401
        
        if not token:
            return {"status": False, "message": "Token is missing"}, 401
        
        try:
            payload = verify_token(token)
            current_user_id = payload["user_id"]
        except Exception as e:
            return {"status": False, "message": str(e)}, 401
        
        # For Flask-RESTX Resource methods, self is first arg, then current_user_id
        return f(self, current_user_id, *args, **kwargs)
    
    return decorated

