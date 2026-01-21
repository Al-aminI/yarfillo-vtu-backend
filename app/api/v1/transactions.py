"""Transaction endpoints."""
from flask_restx import Namespace, Resource
from flask import request
from app.services.transaction_service import TransactionService
from app.utils.response import success_response, error_response
from app.utils.security import token_required
from app.errors.exceptions import BaseAPIException
from app.api.v1.schemas import transaction_model, success_response_model, error_response_model

ns = Namespace('transactions', description='Transaction operations')
transaction_service = TransactionService()


@ns.route('')
class GetTransactions(Resource):
    @ns.doc('get_transactions', security='Bearer')
    @ns.param('type', 'Transaction type filter (airtime, data, credit)', required=False, enum=['airtime', 'data', 'credit'])
    @ns.param('limit', 'Number of results per page', required=False, type=int, default=50)
    @ns.param('offset', 'Number of results to skip', required=False, type=int, default=0)
    @ns.marshal_with(success_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(500, 'Server error', error_response_model)
    @token_required
    def get(self, current_user_id):
        """Get user transactions with optional filtering."""
        try:
            transaction_type = request.args.get("type")  # airtime, data, credit
            limit = int(request.args.get("limit", 50))
            offset = int(request.args.get("offset", 0))
            
            result = transaction_service.get_transactions(
                user_id=current_user_id,
                transaction_type=transaction_type,
                limit=limit,
                offset=offset
            )
            
            return {
                "status": True,
                "message": "Transactions retrieved successfully",
                "data": result
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500


@ns.route('/<string:transaction_id>')
@ns.param('transaction_id', 'Transaction ID')
class GetTransaction(Resource):
    @ns.doc('get_transaction', security='Bearer')
    @ns.marshal_with(success_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(404, 'Transaction not found', error_response_model)
    @token_required
    def get(self, current_user_id, transaction_id):
        """Get a specific transaction by ID."""
        try:
            transaction = transaction_service.get_transaction(transaction_id, current_user_id)
            return {
                "status": True,
                "message": "Transaction retrieved successfully",
                "data": transaction.to_dict()
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500
