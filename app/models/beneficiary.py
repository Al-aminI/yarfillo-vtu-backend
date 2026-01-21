"""Beneficiary model."""
from datetime import datetime
from app.extensions import db


class Beneficiary(db.Model):
    """Beneficiary model."""
    __tablename__ = "beneficiaries"
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False, index=True)
    network = db.Column(db.String(20), nullable=False)  # mtn, glo, airtel, 9mobile
    name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship("User", back_populates="beneficiaries")
    
    # Unique constraint: one beneficiary per user per phone
    __table_args__ = (db.UniqueConstraint("user_id", "phone", name="unique_user_phone"),)
    
    def __init__(self, user_id: str, phone: str, network: str, name: str = None):
        """Initialize beneficiary."""
        from app.utils.helpers import generate_uuid
        self.id = generate_uuid()
        self.user_id = user_id
        self.phone = phone
        self.network = network.lower()
        self.name = name
    
    def to_dict(self) -> dict:
        """Convert beneficiary to dictionary."""
        return {
            "id": self.id,
            "phone": self.phone,
            "network": self.network,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f"<Beneficiary {self.phone} - {self.network}>"

