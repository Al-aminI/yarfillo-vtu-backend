"""Beneficiary endpoints."""
from flask_restx import Namespace, Resource
from flask import request
from app.services.beneficiary_service import BeneficiaryService
from app.utils.response import success_response, error_response
from app.utils.security import token_required
from app.errors.exceptions import BaseAPIException
from app.api.v1.schemas import beneficiary_model, create_beneficiary_model, success_response_model, error_response_model

ns = Namespace('beneficiaries', description='Beneficiary management operations')
beneficiary_service = BeneficiaryService()


@ns.route('')
class Beneficiaries(Resource):
    @ns.doc('get_beneficiaries', security='Bearer')
    @ns.marshal_with(success_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @token_required
    def get(self, current_user_id):
        """Get all beneficiaries for the current user."""
        try:
            beneficiaries = beneficiary_service.get_beneficiaries(current_user_id)
            return {
                "status": True,
                "message": "Beneficiaries retrieved successfully",
                "data": {"beneficiaries": beneficiaries}
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500
    
    @ns.doc('create_beneficiary', security='Bearer')
    @ns.expect(create_beneficiary_model)
    @ns.marshal_with(success_response_model, code=201)
    @ns.response(400, 'Validation error', error_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(500, 'Server error', error_response_model)
    @token_required
    def post(self, current_user_id):
        """Create a new beneficiary."""
        try:
            data = request.get_json()
            
            if not data:
                return {"status": False, "message": "Request body is required"}, 400
            
            phone = data.get("phone")
            network = data.get("network")
            name = data.get("name")
            
            if not phone:
                return {"status": False, "message": "phone is required"}, 400
            
            beneficiary = beneficiary_service.create_beneficiary(
                user_id=current_user_id,
                phone=phone,
                network=network,
                name=name
            )
            
            return {
                "status": True,
                "message": "Beneficiary created successfully",
                "data": beneficiary
            }, 201
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500


@ns.route('/<string:beneficiary_id>')
@ns.param('beneficiary_id', 'Beneficiary ID')
class Beneficiary(Resource):
    @ns.doc('delete_beneficiary', security='Bearer')
    @ns.marshal_with(success_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(404, 'Beneficiary not found', error_response_model)
    @token_required
    def delete(self, current_user_id, beneficiary_id):
        """Delete a beneficiary."""
        try:
            result = beneficiary_service.delete_beneficiary(beneficiary_id, current_user_id)
            return {
                "status": True,
                "message": "Beneficiary deleted successfully",
                "data": result
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500
