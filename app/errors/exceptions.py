"""Custom exception classes."""


class BaseAPIException(Exception):
    """Base exception for API errors."""
    status_code = 400
    message = "An error occurred"
    
    def __init__(self, message: str = None, status_code: int = None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class InsufficientBalanceException(BaseAPIException):
    """Raised when wallet balance is insufficient."""
    status_code = 400
    message = "Insufficient wallet balance"


class InvalidTransactionException(BaseAPIException):
    """Raised when transaction is invalid."""
    status_code = 400
    message = "Invalid transaction"


class PayscribeAPIException(BaseAPIException):
    """Raised when Payscribe API call fails."""
    status_code = 502
    message = "External API error"


class TokenExpiredException(BaseAPIException):
    """Raised when JWT token has expired."""
    status_code = 401
    message = "Token has expired"


class InvalidTokenException(BaseAPIException):
    """Raised when JWT token is invalid."""
    status_code = 401
    message = "Invalid token"


class NotFoundException(BaseAPIException):
    """Raised when resource is not found."""
    status_code = 404
    message = "Resource not found"


class ValidationException(BaseAPIException):
    """Raised when validation fails."""
    status_code = 400
    message = "Validation error"

