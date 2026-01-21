"""User model."""
from datetime import datetime
from typing import Optional
from app.extensions import db
from app.utils.security import hash_pin


class User(db.Model):
    """User model."""
    __tablename__ = "users"
    
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    pin_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    wallet = db.relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    transactions = db.relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    beneficiaries = db.relationship("Beneficiary", back_populates="user", cascade="all, delete-orphan")
    
    def __init__(self, email: str, phone: str, first_name: str, last_name: str, pin: str):
        """Initialize user with hashed PIN."""
        from app.utils.helpers import generate_uuid
        self.id = generate_uuid()
        self.email = email
        self.phone = phone
        self.first_name = first_name
        self.last_name = last_name
        self.pin_hash = hash_pin(pin)
    
    def verify_pin(self, pin: str) -> bool:
        """Verify user PIN."""
        from app.utils.security import verify_pin
        return verify_pin(pin, self.pin_hash)
    
    def to_dict(self, include_wallet: bool = False) -> dict:
        """Convert user to dictionary."""
        data = {
            "id": self.id,
            "email": self.email,
            "phone": self.phone,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        if include_wallet and self.wallet:
            data["wallet"] = self.wallet.to_dict()
        return data
    
    def __repr__(self):
        return f"<User {self.email}>"

