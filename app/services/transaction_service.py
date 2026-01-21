"""Transaction service."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models import Transaction
from app.errors.exceptions import NotFoundException


class TransactionService:
    """Service for transaction operations."""
    
    def get_transactions(
        self,
        user_id: str,
        transaction_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get user transactions with optional filtering."""
        query = Transaction.query.filter_by(user_id=user_id)
        
        if transaction_type:
            query = query.filter_by(type=transaction_type)
        
        # Order by created_at descending
        query = query.order_by(Transaction.created_at.desc())
        
        total = query.count()
        transactions = query.limit(limit).offset(offset).all()
        
        return {
            "transactions": [t.to_dict() for t in transactions],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def get_transaction(self, transaction_id: str, user_id: str) -> Transaction:
        """Get a specific transaction."""
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
        if not transaction:
            raise NotFoundException("Transaction not found")
        return transaction

