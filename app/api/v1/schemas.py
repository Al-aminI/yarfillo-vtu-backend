"""API request/response schemas for Swagger documentation."""
from flask_restx import fields, Model

# Auth Schemas
signup_model = Model('Signup', {
    'email': fields.String(required=True, description='User email address'),
    'phone': fields.String(required=True, description='User phone number'),
    'first_name': fields.String(required=True, description='User first name'),
    'last_name': fields.String(required=True, description='User last name'),
    'pin': fields.String(required=True, description='4-digit PIN', min_length=4, max_length=4)
})

login_model = Model('Login', {
    'email': fields.String(required=True, description='User email address'),
    'pin': fields.String(required=True, description='4-digit PIN', min_length=4, max_length=4)
})

# Wallet Schemas
wallet_response = Model('Wallet', {
    'id': fields.String(description='Wallet ID'),
    'balance': fields.Float(description='Wallet balance'),
    'account_number': fields.String(description='Virtual account number'),
    'bank_name': fields.String(description='Bank name'),
    'bank_code': fields.String(description='Bank code'),
    'virtual_account_status': fields.String(description='Account status')
})

# Airtime Schemas
airtime_purchase_model = Model('AirtimePurchase', {
    'network': fields.String(required=True, description='Network (mtn, glo, airtel, 9mobile)', enum=['mtn', 'glo', 'airtel', '9mobile']),
    'amount': fields.Float(required=True, description='Amount (minimum NGN 50)', min=50),
    'phone': fields.String(required=True, description='Phone number to credit'),
    'save_beneficiary': fields.Boolean(description='Save as beneficiary', default=False),
    'beneficiary_name': fields.String(description='Beneficiary name (optional)')
})

# Data Schemas
data_purchase_model = Model('DataPurchase', {
    'network': fields.String(required=True, description='Network (mtn, glo, airtel, 9mobile)', enum=['mtn', 'glo', 'airtel', '9mobile']),
    'plan_id': fields.String(required=True, description='Data plan ID from /data/plans'),
    'phone': fields.String(required=True, description='Phone number to credit'),
    'save_beneficiary': fields.Boolean(description='Save as beneficiary', default=False),
    'beneficiary_name': fields.String(description='Beneficiary name (optional)')
})

# Transaction Schemas
transaction_model = Model('Transaction', {
    'id': fields.String(description='Transaction ID'),
    'type': fields.String(description='Transaction type (airtime, data, credit)', enum=['airtime', 'data', 'credit']),
    'status': fields.String(description='Transaction status', enum=['pending', 'processing', 'success', 'failed', 'refunded']),
    'amount': fields.Float(description='Transaction amount'),
    'reference': fields.String(description='Transaction reference'),
    'details': fields.Raw(description='Transaction details'),
    'description': fields.String(description='Transaction description'),
    'created_at': fields.String(description='Creation timestamp')
})

# Beneficiary Schemas
beneficiary_model = Model('Beneficiary', {
    'id': fields.String(description='Beneficiary ID'),
    'phone': fields.String(description='Phone number'),
    'network': fields.String(description='Network', enum=['mtn', 'glo', 'airtel', '9mobile']),
    'name': fields.String(description='Beneficiary name'),
    'created_at': fields.String(description='Creation timestamp')
})

create_beneficiary_model = Model('CreateBeneficiary', {
    'phone': fields.String(required=True, description='Phone number'),
    'network': fields.String(description='Network (auto-detected if not provided)', enum=['mtn', 'glo', 'airtel', '9mobile']),
    'name': fields.String(description='Beneficiary name (optional)')
})

# User Schemas
user_model = Model('User', {
    'id': fields.String(description='User ID'),
    'email': fields.String(description='Email address'),
    'phone': fields.String(description='Phone number'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'is_active': fields.Boolean(description='Account status'),
    'wallet': fields.Nested(wallet_response, description='Wallet details'),
    'created_at': fields.String(description='Creation timestamp')
})

# Response Schemas
success_response_model = Model('SuccessResponse', {
    'status': fields.Boolean(description='Response status', default=True),
    'message': fields.String(description='Response message'),
    'data': fields.Raw(description='Response data')
})

error_response_model = Model('ErrorResponse', {
    'status': fields.Boolean(description='Response status', default=False),
    'message': fields.String(description='Error message'),
    'errors': fields.Raw(description='Error details (optional)')
})

