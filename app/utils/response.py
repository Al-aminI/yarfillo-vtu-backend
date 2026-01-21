"""Standard response utilities."""
from flask import jsonify
from typing import Any, Optional, Dict


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> tuple:
    """Standard success response."""
    response = {
        "status": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


def error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[Dict] = None
) -> tuple:
    """Standard error response."""
    response = {
        "status": False,
        "message": message
    }
    if errors:
        response["errors"] = errors
    return jsonify(response), status_code

