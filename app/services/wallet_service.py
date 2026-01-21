"""Wallet service."""
from typing import Dict, Any, Optional
from decimal import Decimal
from flask import current_app
from app.extensions import db
from app.models import Wallet, User, Transaction
from app.integrations import PayscribeClient
from app.utils.helpers import generate_ref
from app.errors.exceptions import NotFoundException, ValidationException, InsufficientBalanceException


class WalletService:
    """Service for wallet operations."""
    
    def __init__(self):
        self.payscribe_client = PayscribeClient()
    
    def create_wallet_with_virtual_account(self, user_id: str) -> Wallet:
        """Create wallet and Payscribe virtual account for user."""
        user = User.query.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        # Create wallet
        wallet = Wallet(user_id=user_id)
        db.session.add(wallet)
        db.session.flush()
        
        # Create Payscribe customer
        try:
            customer_response = self.payscribe_client.create_customer(
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                phone=user.phone,
                country="NG"
            )
            
            if not customer_response.get("status"):
                # Check if customer already exists in Payscribe
                error_desc = customer_response.get("description", "").lower()
                if "already exist" in error_desc:
                    # Customer exists in Payscribe - this shouldn't happen if email/phone validation worked
                    # But if it does, we can't create a new account for them
                    raise ValidationException("Customer already exists in Payscribe. Please use a different email or phone.")
                raise ValidationException("Failed to create Payscribe customer")
            
            customer_id = customer_response["message"]["details"]["customer_id"]
            wallet.payscribe_customer_id = customer_id
            
            # Create virtual account
            va_response = self.payscribe_client.create_virtual_account(
                customer_id=customer_id,
                account_type="static",
                currency="NGN",
                banks=["9psb"]  # Can be configured
            )
            
            if not va_response.get("status"):
                error_msg = va_response.get("message", {}).get("description") or "Failed to create virtual account"
                raise ValidationException(f"Failed to create virtual account: {error_msg}")
            
            # Handle account details - can be a list or dict
            account_data = va_response.get("message", {}).get("details", {}).get("account")
            
            if not account_data:
                raise ValidationException("No account details returned from Payscribe")
            
            # If account is a list, take the first one
            if isinstance(account_data, list):
                if len(account_data) == 0:
                    raise ValidationException("Empty account list returned from Payscribe")
                account_details = account_data[0]
            else:
                account_details = account_data
            
            wallet.payscribe_account_id = account_details.get("id") or account_details.get("account_id")
            wallet.payscribe_account_number = account_details.get("account_number")
            wallet.payscribe_bank_code = account_details.get("bank_code")
            wallet.payscribe_bank_name = account_details.get("bank_name")
            wallet.virtual_account_status = "active"
            
            return wallet
        except ValidationException:
            # Re-raise validation exceptions
            raise
        except Exception as e:
            # Log the error but let the exception propagate to auth_service
            # auth_service will handle the rollback
            current_app.logger.error(f"Failed to create virtual account: {str(e)}", exc_info=True)
            raise ValidationException(f"Failed to create virtual account: {str(e)}")
    
    def get_wallet(self, user_id: str) -> Wallet:
        """Get user wallet."""
        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            raise NotFoundException("Wallet not found")
        return wallet
    
    def get_wallet_balance(self, user_id: str) -> Dict[str, Any]:
        """Get wallet balance and account details."""
        wallet = self.get_wallet(user_id)
        return wallet.to_dict()
    
    def credit_wallet(
        self,
        user_id: str,
        amount: Decimal,
        reference: str,
        description: str = "Wallet funding",
        payscribe_trans_id: Optional[str] = None
    ) -> Transaction:
        """Credit wallet balance."""
        wallet = self.get_wallet(user_id)
        
        if not wallet.credit(amount):
            raise ValidationException("Invalid credit amount")
        
        # Create credit transaction
        transaction = Transaction(
            user_id=user_id,
            type="credit",
            amount=amount,
            reference=reference,
            status="success",
            description=description
        )
        transaction.payscribe_transaction_id = payscribe_trans_id
        
        db.session.add(transaction)
        db.session.commit()
        
        return transaction
    
    def debit_wallet(
        self,
        user_id: str,
        amount: Decimal,
        reference: str,
        description: str = "Wallet debit"
    ) -> bool:
        """Debit wallet balance."""
        wallet = self.get_wallet(user_id)
        
        if not wallet.has_sufficient_balance(amount):
            raise InsufficientBalanceException()
        
        if not wallet.debit(amount):
            raise ValidationException("Failed to debit wallet")
        
        db.session.commit()
        return True
    
    def verify_payment(self, account_number: str, amount: float) -> Dict[str, Any]:
        """Verify payment to virtual account."""
        return self.payscribe_client.verify_payment(
            account_number=account_number,
            amount=amount
        )

