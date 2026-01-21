"""Wallet endpoints."""
from flask_restx import Namespace, Resource
from app.services.wallet_service import WalletService
from app.utils.response import success_response, error_response
from app.utils.security import token_required
from app.errors.exceptions import BaseAPIException
from app.api.v1.schemas import wallet_response, success_response_model, error_response_model

ns = Namespace('wallet', description='Wallet operations')
wallet_service = WalletService()


@ns.route('/balance')
class GetBalance(Resource):
    @ns.doc('get_balance', security='Bearer')
    @ns.marshal_with(success_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(404, 'Wallet not found', error_response_model)
    @token_required
    def get(self, current_user_id):
        """Get wallet balance and account details."""
        try:
            wallet = wallet_service.get_wallet_balance(current_user_id)
            return {
                "status": True,
                "message": "Wallet balance retrieved successfully",
                "data": wallet
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500


@ns.route('/account-details')
class GetAccountDetails(Resource):
    @ns.doc('get_account_details', security='Bearer')
    @ns.marshal_with(success_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(404, 'Wallet not found', error_response_model)
    @token_required
    def get(self, current_user_id):
        """Get virtual account details for funding."""
        try:
            wallet = wallet_service.get_wallet_balance(current_user_id)
            
            # Return account details in format expected by frontend
            account_details = {
                "account_number": wallet.get("account_number"),
                "bank_name": wallet.get("bank_name"),
                "bank_code": wallet.get("bank_code"),
                "balance": wallet.get("balance")
            }
            
            return {
                "status": True,
                "message": "Account details retrieved successfully",
                "data": account_details
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500
