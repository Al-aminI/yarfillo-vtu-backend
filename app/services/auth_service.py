"""Authentication service."""
from typing import Dict, Any, Optional
from decimal import Decimal
from app.extensions import db
from app.models import User, Wallet
from app.integrations import PayscribeClient
from app.services.wallet_service import WalletService
from app.utils.security import generate_token, verify_pin
from app.errors.exceptions import ValidationException, NotFoundException


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self):
        self.wallet_service = WalletService()
    
    def signup(
        self,
        email: str,
        phone: str,
        first_name: str,
        last_name: str,
        pin: str
    ) -> Dict[str, Any]:
        """Register a new user and create wallet with virtual account."""
        # Validate inputs
        if not email or not phone or not first_name or not last_name or not pin:
            raise ValidationException("All fields are required")
        
        if len(pin) != 4 or not pin.isdigit():
            raise ValidationException("PIN must be 4 digits")
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            raise ValidationException("Email already registered")
        
        if User.query.filter_by(phone=phone).first():
            raise ValidationException("Phone number already registered")
        
        # Create user
        user = User(
            email=email,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            pin=pin
        )
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Create wallet and virtual account
        try:
            wallet = self.wallet_service.create_wallet_with_virtual_account(user.id)
            db.session.commit()
            
            # Generate token
            token = generate_token(user.id)
            
            return {
                "user": user.to_dict(include_wallet=True),
                "token": token
            }
        except Exception as e:
            db.session.rollback()
            raise ValidationException(f"Failed to create account: {str(e)}")
    
    def login(self, email: str, pin: str) -> Dict[str, Any]:
        """Authenticate user and return token."""
        if not email or not pin:
            raise ValidationException("Email and PIN are required")
        
        user = User.query.filter_by(email=email).first()
        if not user:
            raise NotFoundException("Invalid email or PIN")
        
        if not user.is_active:
            raise ValidationException("Account is deactivated")
        
        if not user.verify_pin(pin):
            raise ValidationException("Invalid email or PIN")
        
        # Generate token
        token = generate_token(user.id)
        
        return {
            "user": user.to_dict(include_wallet=True),
            "token": token
        }
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get user details."""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        return user.to_dict(include_wallet=True)

