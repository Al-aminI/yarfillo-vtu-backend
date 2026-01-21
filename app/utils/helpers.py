"""Helper utility functions."""
import uuid
import random
import string
from typing import Optional


def generate_ref(prefix: Optional[str] = None) -> str:
    """Generate unique reference string."""
    ref = f"{prefix}_" if prefix else ""
    ref += uuid.uuid4().hex[:16].upper()
    return ref


def generate_uuid() -> str:
    """Generate UUID string."""
    return str(uuid.uuid4())


def format_currency(amount: float, currency: str = "NGN") -> str:
    """Format amount as currency."""
    return f"₦{amount:,.2f}"


def format_phone_number(phone: str) -> str:
    """Format phone number to standard format."""
    # Remove all non-digit characters
    phone = "".join(filter(str.isdigit, phone))
    
    # Convert to international format if needed
    if phone.startswith("0"):
        phone = "234" + phone[1:]
    elif not phone.startswith("234"):
        phone = "234" + phone
    
    return phone


def detect_network(phone: str) -> Optional[str]:
    """Detect network from phone number."""
    from app.utils.constants import NETWORK_CODES
    
    # Remove all non-digit characters
    phone = "".join(filter(str.isdigit, phone))
    
    # Get first 4 digits
    if len(phone) >= 4:
        prefix = phone[:4]
        for network, codes in NETWORK_CODES.items():
            if prefix in codes:
                return network.lower()
    
    return None


def validate_phone_number(phone: str) -> bool:
    """Validate Nigerian phone number."""
    phone = "".join(filter(str.isdigit, phone))
    
    # Nigerian numbers are 11 digits (starting with 0) or 13 digits (starting with 234)
    if phone.startswith("234"):
        return len(phone) == 13
    elif phone.startswith("0"):
        return len(phone) == 11
    return False

