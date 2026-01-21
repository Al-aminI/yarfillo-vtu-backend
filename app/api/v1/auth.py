"""Authentication endpoints."""
from flask_restx import Namespace, Resource, fields
from flask import request, current_app
from app.services.auth_service import AuthService
from app.utils.response import success_response, error_response
from app.utils.security import token_required
from app.errors.exceptions import BaseAPIException
from app.api.v1.schemas import signup_model, login_model, user_model, success_response_model, error_response_model

ns = Namespace('auth', description='Authentication operations')
auth_service = AuthService()


@ns.route('/signup')
class Signup(Resource):
    @ns.doc('signup')
    @ns.expect(signup_model)
    @ns.marshal_with(success_response_model, code=201)
    @ns.response(400, 'Validation error', error_response_model)
    @ns.response(500, 'Server error', error_response_model)
    def post(self):
        """Register a new user."""
        try:
            data = request.get_json()
            
            if not data:
                return {"status": False, "message": "Request body is required"}, 400
            
            email = data.get("email")
            phone = data.get("phone")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            pin = data.get("pin")
            
            result = auth_service.signup(
                email=email,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                pin=pin
            )
            
            return {
                "status": True,
                "message": "User registered successfully",
                "data": result
            }, 201
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            current_app.logger.error(f"Signup error: {str(e)}", exc_info=True)
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500


@ns.route('/login')
class Login(Resource):
    @ns.doc('login')
    @ns.expect(login_model)
    @ns.marshal_with(success_response_model)
    @ns.response(400, 'Validation error', error_response_model)
    @ns.response(401, 'Invalid credentials', error_response_model)
    @ns.response(500, 'Server error', error_response_model)
    def post(self):
        """Authenticate user and get JWT token."""
        try:
            data = request.get_json()
            
            if not data:
                return {"status": False, "message": "Request body is required"}, 400
            
            email = data.get("email")
            pin = data.get("pin")
            
            result = auth_service.login(email=email, pin=pin)
            
            return {
                "status": True,
                "message": "Login successful",
                "data": result
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500


@ns.route('/me')
class GetCurrentUser(Resource):
    @ns.doc('get_current_user', security='Bearer')
    @ns.marshal_with(success_response_model)
    @ns.response(401, 'Unauthorized', error_response_model)
    @ns.response(404, 'User not found', error_response_model)
    @token_required
    def get(self, current_user_id):
        """Get current authenticated user details."""
        try:
            user = auth_service.get_user(current_user_id)
            return {
                "status": True,
                "message": "User retrieved successfully",
                "data": user
            }
        except BaseAPIException as e:
            return {"status": False, "message": e.message}, e.status_code
        except Exception as e:
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500
