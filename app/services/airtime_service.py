"""Airtime service."""
from typing import Dict, Any
from decimal import Decimal
from flask import current_app
from app.extensions import db
from app.models import Transaction, Beneficiary
from app.integrations import PayscribeClient
from app.services.wallet_service import WalletService
from app.utils.helpers import generate_ref, format_phone_number, detect_network
from app.utils.constants import NETWORKS
from app.errors.exceptions import ValidationException, InsufficientBalanceException, PayscribeAPIException


class AirtimeService:
    """Service for airtime purchase operations."""
    
    def __init__(self):
        self.payscribe_client = PayscribeClient()
        self.wallet_service = WalletService()
    
    def purchase_airtime(
        self,
        user_id: str,
        network: str,
        amount: Decimal,
        phone: str,
        save_beneficiary: bool = False,
        beneficiary_name: str = None
    ) -> Dict[str, Any]:
        """Purchase airtime for a phone number."""
        # Validate network
        network_lower = network.lower()
        if network_lower not in NETWORKS:
            raise ValidationException(f"Invalid network. Must be one of: {', '.join(NETWORKS.keys())}")
        
        # Validate amount (minimum NGN 50)
        if amount < Decimal("50.00"):
            raise ValidationException("Minimum airtime purchase is NGN 50")
        
        # Format phone number
        formatted_phone = format_phone_number(phone)
        
        # Auto-detect network if not provided or validate
        detected_network = detect_network(formatted_phone)
        if detected_network and detected_network != network_lower:
            # Use detected network if different
            network_lower = detected_network
        
        # Check wallet balance
        wallet = self.wallet_service.get_wallet(user_id)
        if not wallet.has_sufficient_balance(amount):
            raise InsufficientBalanceException()
        
        # Generate reference
        reference = generate_ref("AT")
        
        # Create pending transaction
        transaction = Transaction(
            user_id=user_id,
            type="airtime",
            amount=amount,
            reference=reference,
            status="pending",
            details={
                "network": network_lower,
                "phone": formatted_phone,
                "amount": float(amount)
            },
            description=f"Airtime purchase - {NETWORKS[network_lower]} {formatted_phone}"
        )
        db.session.add(transaction)
        db.session.flush()
        
        try:
            # Debit wallet
            self.wallet_service.debit_wallet(
                user_id=user_id,
                amount=amount,
                reference=reference,
                description=f"Airtime purchase - {formatted_phone}"
            )
            
            # Call Payscribe API
            payscribe_response = self.payscribe_client.vend_airtime(
                network=network_lower,
                amount=float(amount),
                recipient=formatted_phone,
                ref=reference
            )
            
            # Update transaction based on response
            if payscribe_response.get("status"):
                transaction.status = "success"
                transaction.payscribe_transaction_id = payscribe_response.get("message", {}).get("details", {}).get("trans_id")
                transaction.payscribe_reference = payscribe_response.get("message", {}).get("details", {}).get("ref")
            else:
                transaction.status = "failed"
                # Refund wallet
                wallet = self.wallet_service.get_wallet(user_id)
                wallet.credit(amount)
                db.session.commit()
                raise PayscribeAPIException(payscribe_response.get("description", "Airtime purchase failed"))
            
            db.session.commit()
            
            # Save beneficiary if requested
            if save_beneficiary:
                self._save_beneficiary(user_id, formatted_phone, network_lower, beneficiary_name)
            
            return {
                "transaction": transaction.to_dict(),
                "message": "Airtime purchased successfully"
            }
        except Exception as e:
            db.session.rollback()
            # Refund if wallet was debited
            try:
                wallet = self.wallet_service.get_wallet(user_id)
                if transaction and transaction.status in ["pending", "processing"]:
                    wallet.credit(amount)
                    transaction.status = "failed"
                    db.session.commit()
            except Exception as refund_error:
                db.session.rollback()
                current_app.logger.error(f"Error refunding wallet: {str(refund_error)}")
            raise e
    
    def _save_beneficiary(
        self,
        user_id: str,
        phone: str,
        network: str,
        name: str = None
    ):
        """Save beneficiary if not exists."""
        from app.models import Beneficiary
        
        existing = Beneficiary.query.filter_by(user_id=user_id, phone=phone).first()
        if not existing:
            beneficiary = Beneficiary(
                user_id=user_id,
                phone=phone,
                network=network,
                name=name
            )
            db.session.add(beneficiary)
            db.session.commit()

