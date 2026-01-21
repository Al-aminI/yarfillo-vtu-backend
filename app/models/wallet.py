"""Wallet model."""
from datetime import datetime
from decimal import Decimal
from app.extensions import db
from app.utils.constants import VIRTUAL_ACCOUNT_STATUSES


class Wallet(db.Model):
    """Wallet model."""
    __tablename__ = "wallets"
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    balance = db.Column(db.Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    
    # Payscribe Virtual Account fields
    payscribe_customer_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    payscribe_account_id = db.Column(db.String(255), unique=True, nullable=True, index=True)
    payscribe_account_number = db.Column(db.String(20), unique=True, nullable=True, index=True)
    payscribe_bank_code = db.Column(db.String(10), nullable=True)
    payscribe_bank_name = db.Column(db.String(100), nullable=True)
    virtual_account_status = db.Column(db.String(20), default="active", nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship("User", back_populates="wallet")
    
    def __init__(self, user_id: str):
        """Initialize wallet."""
        from app.utils.helpers import generate_uuid
        self.id = generate_uuid()
        self.user_id = user_id
        self.balance = Decimal("0.00")
        self.virtual_account_status = "active"
    
    def credit(self, amount: Decimal) -> bool:
        """Credit wallet balance."""
        if amount <= 0:
            return False
        self.balance += amount
        return True
    
    def debit(self, amount: Decimal) -> bool:
        """Debit wallet balance."""
        if amount <= 0 or self.balance < amount:
            return False
        self.balance -= amount
        return True
    
    def has_sufficient_balance(self, amount: Decimal) -> bool:
        """Check if wallet has sufficient balance."""
        return self.balance >= amount
    
    def to_dict(self) -> dict:
        """Convert wallet to dictionary."""
        return {
            "id": self.id,
            "balance": float(self.balance),
            "account_number": self.payscribe_account_number,
            "bank_name": self.payscribe_bank_name,
            "bank_code": self.payscribe_bank_code,
            "virtual_account_status": self.virtual_account_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f"<Wallet {self.user_id} - Balance: {self.balance}>"

