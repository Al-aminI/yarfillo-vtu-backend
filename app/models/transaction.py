"""Transaction model."""
from datetime import datetime
from decimal import Decimal
from app.extensions import db
from app.utils.constants import TRANSACTION_TYPES, TRANSACTION_STATUSES


class Transaction(db.Model):
    """Transaction model."""
    __tablename__ = "transactions"
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False, index=True)  # airtime, data, credit
    status = db.Column(db.String(20), default="pending", nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reference = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Payscribe transaction details
    payscribe_transaction_id = db.Column(db.String(255), nullable=True, index=True)
    payscribe_reference = db.Column(db.String(255), nullable=True)
    
    # Transaction-specific details (JSON)
    details = db.Column(db.JSON, nullable=True)
    
    # Metadata
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship("User", back_populates="transactions")
    
    def __init__(
        self,
        user_id: str,
        type: str,
        amount: Decimal,
        reference: str,
        details: dict = None,
        description: str = None,
        status: str = "pending"
    ):
        """Initialize transaction."""
        from app.utils.helpers import generate_uuid
        if type not in TRANSACTION_TYPES:
            raise ValueError(f"Invalid transaction type: {type}")
        if status not in TRANSACTION_STATUSES:
            raise ValueError(f"Invalid transaction status: {status}")
        
        self.id = generate_uuid()
        self.user_id = user_id
        self.type = type
        self.amount = amount
        self.reference = reference
        self.status = status
        self.details = details or {}
        self.description = description
    
    def update_status(self, status: str):
        """Update transaction status."""
        if status not in TRANSACTION_STATUSES:
            raise ValueError(f"Invalid transaction status: {status}")
        self.status = status
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "amount": float(self.amount),
            "reference": self.reference,
            "payscribe_transaction_id": self.payscribe_transaction_id,
            "payscribe_reference": self.payscribe_reference,
            "details": self.details,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f"<Transaction {self.reference} - {self.type} - {self.status}>"

