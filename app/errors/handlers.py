"""Error handlers for Flask application."""
from flask import jsonify
from app.errors.exceptions import BaseAPIException


def register_error_handlers(app):
    """Register error handlers with Flask app."""
    
    @app.errorhandler(BaseAPIException)
    def handle_api_exception(e):
        return jsonify({
            "status": False,
            "message": e.message
        }), e.status_code
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            "status": False,
            "message": "Resource not found"
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        return jsonify({
            "status": False,
            "message": "Internal server error"
        }), 500
    
    @app.errorhandler(422)
    def handle_unprocessable_entity(e):
        return jsonify({
            "status": False,
            "message": "Unprocessable entity"
        }), 422

