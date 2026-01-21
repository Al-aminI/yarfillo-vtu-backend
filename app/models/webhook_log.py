"""Webhook log model."""
from datetime import datetime
from app.extensions import db


class WebhookLog(db.Model):
    """Webhook log model for tracking incoming webhooks."""
    __tablename__ = "webhook_logs"
    
    id = db.Column(db.String(36), primary_key=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)
    payload = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False, index=True)  # pending, processed, failed
    error_message = db.Column(db.Text, nullable=True)
    processed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, event_type: str, payload: dict):
        """Initialize webhook log."""
        from app.utils.helpers import generate_uuid
        self.id = generate_uuid()
        self.event_type = event_type
        self.payload = payload
        self.status = "pending"
    
    def mark_processed(self):
        """Mark webhook as processed."""
        self.status = "processed"
        self.processed_at = datetime.utcnow()
    
    def mark_failed(self, error_message: str):
        """Mark webhook as failed."""
        self.status = "failed"
        self.error_message = error_message
        self.processed_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert webhook log to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }
    
    def __repr__(self):
        return f"<WebhookLog {self.event_type} - {self.status}>"

