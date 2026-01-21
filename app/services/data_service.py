"""Data service."""
from typing import Dict, Any, List
from decimal import Decimal
from flask import current_app
from app.extensions import db
from app.models import Transaction, Beneficiary
from app.integrations import PayscribeClient
from app.services.wallet_service import WalletService
from app.utils.helpers import generate_ref, format_phone_number, detect_network
from app.utils.constants import NETWORKS
from app.errors.exceptions import ValidationException, InsufficientBalanceException, PayscribeAPIException


class DataService:
    """Service for data purchase operations."""
    
    def __init__(self):
        self.payscribe_client = PayscribeClient()
        self.wallet_service = WalletService()
    
    def get_data_plans(self, network: str, category: str = None) -> List[Dict[str, Any]]:
        """Get available data plans for a network."""
        network_lower = network.lower()
        if network_lower not in NETWORKS:
            raise ValidationException(f"Invalid network. Must be one of: {', '.join(NETWORKS.keys())}")
        
        try:
            response = self.payscribe_client.lookup_data_plans(
                network=network_lower,
                category=category
            )
            
            if not response.get("status"):
                raise PayscribeAPIException(response.get("description", "Failed to fetch data plans"))
            
            # Response structure: message.details is an array with network objects
            # Each network object has a "plans" array
            details = response.get("message", {}).get("details", [])
            
            if not details:
                raise PayscribeAPIException("No data plans found")
            
            # Extract plans from the first network object (should match the requested network)
            network_data = details[0] if isinstance(details, list) else details
            plans = network_data.get("plans", [])
            
            if not plans:
                raise PayscribeAPIException("No plans found for this network")
            
            # Format plans for frontend
            formatted_plans = []
            for plan in plans:
                plan_name = plan.get("name", "")
                formatted_plans.append({
                    "id": plan.get("plan_code"),  # Use plan_code, not plan_id
                    "size": self._extract_size(plan_name),
                    "duration": self._extract_duration(plan_name) or "30 Days",  # Default duration
                    "price": float(plan.get("amount", 0)),
                    "validity": self._extract_duration(plan_name) or "30 Days"
                })
            
            return formatted_plans
        except Exception as e:
            raise PayscribeAPIException(f"Failed to fetch data plans: {str(e)}")
    
    def purchase_data(
        self,
        user_id: str,
        network: str,
        plan_id: str,
        phone: str,
        save_beneficiary: bool = False,
        beneficiary_name: str = None
    ) -> Dict[str, Any]:
        """Purchase data bundle for a phone number."""
        # Validate network
        network_lower = network.lower()
        if network_lower not in NETWORKS:
            raise ValidationException(f"Invalid network. Must be one of: {', '.join(NETWORKS.keys())}")
        
        # Get plan details to get amount
        plans = self.get_data_plans(network_lower)
        plan = next((p for p in plans if p["id"] == plan_id), None)
        
        if not plan:
            raise ValidationException("Invalid data plan")
        
        amount = Decimal(str(plan["price"]))  # Use "price" field from formatted response
        
        # Format phone number
        formatted_phone = format_phone_number(phone)
        
        # Auto-detect network if not provided or validate
        detected_network = detect_network(formatted_phone)
        if detected_network and detected_network != network_lower:
            network_lower = detected_network
        
        # Check wallet balance
        wallet = self.wallet_service.get_wallet(user_id)
        if not wallet.has_sufficient_balance(amount):
            raise InsufficientBalanceException()
        
        # Generate reference
        reference = generate_ref("DT")
        
        # Create pending transaction
        transaction = Transaction(
            user_id=user_id,
            type="data",
            amount=amount,
            reference=reference,
            status="pending",
            details={
                "network": network_lower,
                "phone": formatted_phone,
                "plan_id": plan_id,
                "plan_size": plan.get("size", ""),
                "amount": float(amount)
            },
            description=f"Data purchase - {plan.get('size', '')} for {formatted_phone}"
        )
        db.session.add(transaction)
        db.session.flush()
        
        try:
            # Debit wallet
            self.wallet_service.debit_wallet(
                user_id=user_id,
                amount=amount,
                reference=reference,
                description=f"Data purchase - {formatted_phone}"
            )
            
            # Call Payscribe API
            payscribe_response = self.payscribe_client.vend_data(
                network=network_lower,
                plan=plan_id,
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
                raise PayscribeAPIException(payscribe_response.get("description", "Data purchase failed"))
            
            db.session.commit()
            
            # Save beneficiary if requested
            if save_beneficiary:
                self._save_beneficiary(user_id, formatted_phone, network_lower, beneficiary_name)
            
            return {
                "transaction": transaction.to_dict(),
                "message": "Data purchased successfully"
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
    
    def _extract_size(self, plan_name: str) -> str:
        """Extract data size from plan name (e.g., '1GB', '500MB')."""
        import re
        # Look for patterns like "1GB", "500MB", "2.5GB", etc.
        match = re.search(r'(\d+(?:\.\d+)?)\s*(GB|MB|TB)', plan_name, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        return ""
    
    def _extract_duration(self, plan_name: str) -> str:
        """Extract duration from plan name (e.g., '30 days', 'Monthly')."""
        import re
        # Look for patterns like "30 days", "Monthly", "Weekly", etc.
        match = re.search(r'(\d+\s*(?:day|days|month|months|week|weeks))|(monthly|weekly|daily)', plan_name, re.IGNORECASE)
        if match:
            return match.group(0)
        return ""
    
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

