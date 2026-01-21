"""Application constants."""

# Networks
NETWORKS = {
    "mtn": "MTN",
    "glo": "GLO",
    "airtel": "AIRTEL",
    "9mobile": "9MOBILE"
}

NETWORK_CODES = {
    "MTN": ["0803", "0806", "0703", "0706", "0813", "0816", "0810", "0814", "0903", "0906"],
    "GLO": ["0805", "0807", "0705", "0815", "0811", "0905"],
    "AIRTEL": ["0802", "0808", "0708", "0812", "0901", "0902", "0904", "0907"],
    "9MOBILE": ["0809", "0817", "0818", "0908", "0909"]
}

# Transaction Types
TRANSACTION_TYPES = ["airtime", "data", "credit"]

# Transaction Statuses
TRANSACTION_STATUSES = ["pending", "processing", "success", "failed", "refunded"]

# Virtual Account Status
VIRTUAL_ACCOUNT_STATUSES = ["active", "deactivated"]

