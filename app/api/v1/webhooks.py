"""Webhook endpoints."""
from flask_restx import Namespace, Resource
from flask import request, current_app
from app.services.webhook_service import process_payscribe_webhook
from app.utils.security import verify_webhook_ip
from app.models.webhook_log import WebhookLog
from app.extensions import db
from app.api.v1.schemas import success_response_model, error_response_model

ns = Namespace('webhooks', description='Webhook endpoints', security=None)


@ns.route('/payscribe')
class PayscribeWebhook(Resource):
    @ns.doc('payscribe_webhook', description='Handle Payscribe webhook events')
    @ns.response(200, 'Webhook received', success_response_model)
    @ns.response(400, 'Invalid payload', error_response_model)
    @ns.response(401, 'Unauthorized IP', error_response_model)
    @ns.response(500, 'Server error', error_response_model)
    @ns.param('skip_auth', 'Skip authentication for webhooks', _in='header', required=False)
    def post(self):
        """Handle Payscribe webhook events for virtual account payments and transaction updates."""
        try:
            # Get client IP
            client_ip = request.remote_addr or request.environ.get("HTTP_X_FORWARDED_FOR", "").split(",")[0]
            
            # Verify IP (optional in development, required in production)
            if not current_app.config.get("DEBUG", False):
                if not verify_webhook_ip(client_ip):
                    current_app.logger.warning(f"Webhook request from unauthorized IP: {client_ip}")
                    return {"status": False, "message": "Unauthorized"}, 401
            
            # Get payload
            payload = request.get_json()
            if not payload:
                return {"status": False, "message": "Invalid payload"}, 400
            
            # Get event type - Payscribe uses "event_type" field
            event_type = payload.get("event_type") or payload.get("event") or payload.get("type") or "unknown"
            
            # Log webhook
            webhook_log = WebhookLog(event_type=event_type, payload=payload)
            db.session.add(webhook_log)
            db.session.commit()

            # Process webhook synchronously
            process_payscribe_webhook(webhook_log)

            return {"status": True, "message": "Webhook processed", "data": {"message": "Webhook received"}}, 200
        except Exception as e:
            current_app.logger.error(f"Webhook error: {str(e)}")
            return {"status": False, "message": f"An error occurred: {str(e)}"}, 500
