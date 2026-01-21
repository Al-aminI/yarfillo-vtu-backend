"""Airtime endpoints."""
from flask_restx import Namespace, Resource
from decimal import Decimal
from flask import request
from app.services.airtime_service import AirtimeService
from app.utils.response import success_response, error_response
from app.utils.security import token_required
from app.errors.exceptions import BaseAPIException
from app.api.v1.schemas import airtime_purchase_model, success_response_model, error_response_model

ns = Namespace('airtime', description='Airtime purchase operations')
airtime_service = AirtimeService()


@ns.route('/purchase')
class PurchaseAirtime(Resource):
    @ns.doc('purchase_airtime', security='Bearer')
    @ns.expect(airtime_purchase_model)
    @ns.marshal_with(success_response_model)
    @ns.response(400, 'Validation error or insufficient balance', error_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(500, 'Server error', error_response_model)
    @token_required
    def post(self, current_user_id):
        """Purchase airtime for a phone number."""
        try:
            data = request.get_json()
            
            if not data:
                return {"status": False, "message": "Request body is required"}, 400
            
            network = data.get("network")
            amount = data.get("amount")
            phone = data.get("phone")
            save_beneficiary = data.get("save_beneficiary", False)
            beneficiary_name = data.get("beneficiary_name")
            
            if not network or not amount or not phone:
                return {"status": False, "message": "network, amount, and phone are required"}, 400
            
            result = airtime_service.purchase_airtime(
                user_id=current_user_id,
                network=network,
                amount=Decimal(str(amount)),
                phone=phone,
                save_beneficiary=save_beneficiary,
                beneficiary_name=beneficiary_name
            )
            
            return {
                "status": True,
                "message": "Airtime purchased successfully",
                "data": result
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500
