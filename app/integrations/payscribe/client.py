"""Payscribe API client."""
import requests
from typing import Dict, Any, Optional, List
from flask import current_app
from app.errors.exceptions import PayscribeAPIException


class PayscribeClient:
    """Client for interacting with Payscribe API."""
    
    def __init__(self):
        """Initialize Payscribe client with config."""
        # Don't access current_app here - will be accessed lazily
        self._base_url = None
        self._api_token = None
        self._secret_key = None
        self._headers = None
    
    @property
    def base_url(self):
        """Get base URL from config."""
        if self._base_url is None:
            self._base_url = current_app.config.get("PAYSCRIBE_BASE_URL", "https://api.payscribe.ng/api/v1")
        return self._base_url
    
    @property
    def api_token(self):
        """Get API token from config."""
        if self._api_token is None:
            self._api_token = current_app.config.get("PAYSCRIBE_API_TOKEN", "ps_pk_test_5fJUELCWRxbYyqE0mylVlfeekNK9iY0990")
        return self._api_token
    
    @property
    def secret_key(self):
        """Get secret key from config."""
        if self._secret_key is None:
            self._secret_key = current_app.config.get("PAYSCRIBE_SECRET_KEY", "")
        return self._secret_key
    
    @property
    def headers(self):
        """Get headers with auth token."""
        if self._headers is None:
            self._headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
        return self._headers
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Payscribe API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                # If response is not JSON, raise with text
                raise PayscribeAPIException(f"Invalid JSON response: {response.text}")
            
            # Check if Payscribe returned an error in the response body
            if not response_data.get("status") and response.status_code not in [200, 201]:
                error_msg = response_data.get("description") or response_data.get("message") or "Unknown error"
                raise PayscribeAPIException(f"Payscribe API error: {error_msg}")
            
            # For non-200 status codes, check if it's a pending transaction (201)
            if response.status_code == 201:
                # Transaction pending - this is acceptable for some endpoints
                return response_data
            
            # Raise for other HTTP errors
            if response.status_code >= 400:
                error_msg = response_data.get("description") or response_data.get("message") or response.text
                raise PayscribeAPIException(f"Payscribe API error ({response.status_code}): {error_msg}")
            
            return response_data
        except PayscribeAPIException:
            raise
        except requests.exceptions.RequestException as e:
            raise PayscribeAPIException(f"Payscribe API request error: {str(e)}")
        except Exception as e:
            raise PayscribeAPIException(f"Unexpected error: {str(e)}")
    
    # Customer Management
    def create_customer(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        country: str = "NG"
    ) -> Dict[str, Any]:
        """Create a customer in Payscribe (Tier 0)."""
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "country": country
        }
        return self._make_request("POST", "customers/create", data=data)
    
    # Virtual Account Management
    def create_virtual_account(
        self,
        customer_id: str,
        account_type: str = "static",
        currency: str = "NGN",
        banks: List[str] = None
    ) -> Dict[str, Any]:
        """Create a permanent virtual account for a customer."""
        if banks is None:
            banks = ["9psb"]  # Default to 9PSB
        
        data = {
            "account_type": account_type,
            "currency": currency,
            "customer_id": customer_id,
            "bank": banks
        }
        return self._make_request("POST", "collections/virtual-accounts/create", data=data)
    
    def get_virtual_account(self, account_number: str) -> Dict[str, Any]:
        """Get virtual account details."""
        return self._make_request("GET", f"collections/virtual-accounts/{account_number}")
    
    def verify_payment(
        self,
        account_number: str,
        amount: float,
        session_id: Optional[str] = None,
        trans_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Verify payment to virtual account."""
        data = {
            "account_number": account_number,
            "amount": amount
        }
        if session_id:
            data["session_id"] = session_id
        if trans_id:
            data["trans_id"] = trans_id
        
        return self._make_request("POST", "collections/virtual-accounts/confirm-payment", data=data)
    
    # Airtime
    def vend_airtime(
        self,
        network: str,
        amount: float,
        recipient: str,
        ref: Optional[str] = None,
        ported: bool = False
    ) -> Dict[str, Any]:
        """Vend airtime to a phone number."""
        data = {
            "network": network.lower(),
            "amount": amount,
            "recipient": recipient,
            "ported": ported
        }
        if ref:
            data["ref"] = ref
        
        return self._make_request("POST", "airtime", data=data)
    
    # Data Bundle
    def lookup_data_plans(
        self,
        network: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Lookup data plans for a network."""
        params = {"network": network.lower()}
        if category:
            params["category"] = category
        
        return self._make_request("GET", "data/lookup", params=params)
    
    def vend_data(
        self,
        network: str,
        plan: str,
        recipient: str,
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Vend data bundle to a phone number."""
        data = {
            "network": network.lower(),
            "plan": plan,
            "recipient": recipient
        }
        if ref:
            data["ref"] = ref
        
        return self._make_request("POST", "data/vend", data=data)

