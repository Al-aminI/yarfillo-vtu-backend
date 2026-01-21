"""Beneficiary service."""
from typing import Dict, Any, List
from app.extensions import db
from app.models import Beneficiary
from app.utils.helpers import format_phone_number, detect_network
from app.errors.exceptions import ValidationException, NotFoundException


class BeneficiaryService:
    """Service for beneficiary operations."""
    
    def get_beneficiaries(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all beneficiaries for a user."""
        beneficiaries = Beneficiary.query.filter_by(user_id=user_id).order_by(Beneficiary.created_at.desc()).all()
        return [b.to_dict() for b in beneficiaries]
    
    def create_beneficiary(
        self,
        user_id: str,
        phone: str,
        network: str,
        name: str = None
    ) -> Dict[str, Any]:
        """Create a new beneficiary."""
        # Format phone
        formatted_phone = format_phone_number(phone)
        
        # Auto-detect network if not provided
        if not network:
            network = detect_network(formatted_phone)
            if not network:
                raise ValidationException("Could not detect network. Please specify network.")
        
        network_lower = network.lower()
        
        # Check if beneficiary already exists
        existing = Beneficiary.query.filter_by(user_id=user_id, phone=formatted_phone).first()
        if existing:
            raise ValidationException("Beneficiary already exists")
        
        beneficiary = Beneficiary(
            user_id=user_id,
            phone=formatted_phone,
            network=network_lower,
            name=name
        )
        
        db.session.add(beneficiary)
        db.session.commit()
        
        return beneficiary.to_dict()
    
    def delete_beneficiary(self, beneficiary_id: str, user_id: str):
        """Delete a beneficiary."""
        beneficiary = Beneficiary.query.filter_by(id=beneficiary_id, user_id=user_id).first()
        if not beneficiary:
            raise NotFoundException("Beneficiary not found")
        
        db.session.delete(beneficiary)
        db.session.commit()
        
        return {"message": "Beneficiary deleted successfully"}

