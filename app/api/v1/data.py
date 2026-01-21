"""Data endpoints."""
from flask_restx import Namespace, Resource
from flask import request
from app.services.data_service import DataService
from app.utils.response import success_response, error_response
from app.utils.security import token_required
from app.errors.exceptions import BaseAPIException
from app.api.v1.schemas import data_purchase_model, success_response_model, error_response_model

ns = Namespace('data', description='Data bundle operations')
data_service = DataService()


@ns.route('/plans')
class GetDataPlans(Resource):
    @ns.doc('get_data_plans', security='Bearer')
    @ns.param('network', 'Network provider (mtn, glo, airtel, 9mobile)', required=True, enum=['mtn', 'glo', 'airtel', '9mobile'])
    @ns.param('category', 'Data plan category (optional)', required=False)
    @ns.marshal_with(success_response_model)
    @ns.response(400, 'Validation error', error_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(500, 'Server error', error_response_model)
    @token_required
    def get(self, current_user_id):
        """Get available data plans for a network."""
        try:
            network = request.args.get("network")
            category = request.args.get("category")
            
            if not network:
                return {"status": False, "message": "network parameter is required"}, 400
            
            plans = data_service.get_data_plans(network=network, category=category)
            
            return {
                "status": True,
                "message": "Data plans retrieved successfully",
                "data": {"plans": plans}
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500


@ns.route('/purchase')
class PurchaseData(Resource):
    @ns.doc('purchase_data', security='Bearer')
    @ns.expect(data_purchase_model)
    @ns.marshal_with(success_response_model)
    @ns.response(400, 'Validation error or insufficient balance', error_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(500, 'Server error', error_response_model)
    @token_required
    def post(self, current_user_id):
        """Purchase data bundle for a phone number."""
        try:
            data = request.get_json()
            
            if not data:
                return {"status": False, "message": "Request body is required"}, 400
            
            network = data.get("network")
            plan_id = data.get("plan_id")
            phone = data.get("phone")
            save_beneficiary = data.get("save_beneficiary", False)
            beneficiary_name = data.get("beneficiary_name")
            
            if not network or not plan_id or not phone:
                return {"status": False, "message": "network, plan_id, and phone are required"}, 400
            
            result = data_service.purchase_data(
                user_id=current_user_id,
                network=network,
                plan_id=plan_id,
                phone=phone,
                save_beneficiary=save_beneficiary,
                beneficiary_name=beneficiary_name
            )
            
            return {
                "status": True,
                "message": "Data purchased successfully",
                "data": result
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500
