"""API v1 routes."""
from flask import Blueprint
from flask_restx import Api
from app.api.v1 import auth, wallet, airtime, data, transactions, beneficiaries, webhooks
from app.api.v1.schemas import (
    signup_model, login_model, user_model, wallet_response,
    airtime_purchase_model, data_purchase_model, transaction_model,
    beneficiary_model, create_beneficiary_model,
    success_response_model, error_response_model
)

# Create main API blueprint
api_bp = Blueprint("api_v1", __name__)

# Create Flask-RESTX API instance
api = Api(
    api_bp,
    version='1.0',
    title='Yarfillo VTU API',
    description='Backend API for Yarfillo VTU Platform - Airtime, Data, and Wallet Management',
    doc='/docs',  # Swagger UI endpoint (relative to blueprint prefix)
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
        }
    },
    security='Bearer'
)

# Register namespaces
api.add_namespace(auth.ns, path='/auth')
api.add_namespace(wallet.ns, path='/wallet')
api.add_namespace(airtime.ns, path='/airtime')
api.add_namespace(data.ns, path='/data')
api.add_namespace(transactions.ns, path='/transactions')
api.add_namespace(beneficiaries.ns, path='/beneficiaries')
# Webhooks namespace - no authentication required
webhooks_ns = webhooks.ns
webhooks_ns.security = None  # Disable authentication for webhooks
api.add_namespace(webhooks_ns, path='/webhooks')

# Register models for documentation
api.models[signup_model.name] = signup_model
api.models[login_model.name] = login_model
api.models[user_model.name] = user_model
api.models[wallet_response.name] = wallet_response
api.models[airtime_purchase_model.name] = airtime_purchase_model
api.models[data_purchase_model.name] = data_purchase_model
api.models[transaction_model.name] = transaction_model
api.models[beneficiary_model.name] = beneficiary_model
api.models[create_beneficiary_model.name] = create_beneficiary_model
api.models[success_response_model.name] = success_response_model
api.models[error_response_model.name] = error_response_model
