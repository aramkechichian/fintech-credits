"""
Endpoint to friendly name mapper for logs
Maps technical endpoints to user-friendly translated names
"""
from typing import Dict, Optional, List

# Endpoint to translation key mapping
ENDPOINT_TO_MODULE_KEY: Dict[str, str] = {
    "/credit-requests": "creditRequests",
    "/credit-requests/search": "creditRequests",
    "/country-rules": "countryRules",
    "/auth/login": "authentication",
    "/auth/register": "authentication",
    "/auth/me": "authentication",
    "/bank-provider/information": "bankProvider",
    "/data/export/excel": "audits",
    "/logs/search": "logs",
    "/logs/export/excel": "logs",
}

# List of all modules that are logged (for filter dropdown)
# Only creditRequests is currently being logged
LOGGED_MODULES: List[str] = [
    "creditRequests",
]

def get_module_name_for_endpoint(endpoint: str) -> Optional[str]:
    """
    Get the module translation key for an endpoint
    
    Args:
        endpoint: Technical endpoint path (e.g., "/credit-requests")
        
    Returns:
        Translation key for the module name, or None if not found
    """
    # Try exact match first
    if endpoint in ENDPOINT_TO_MODULE_KEY:
        return ENDPOINT_TO_MODULE_KEY[endpoint]
    
    # Try prefix match (e.g., "/credit-requests/{id}" -> "creditRequests")
    for endpoint_prefix, module_key in ENDPOINT_TO_MODULE_KEY.items():
        if endpoint.startswith(endpoint_prefix):
            return module_key
    
    return None


def get_endpoints_for_module(module_key: str) -> List[str]:
    """
    Get all endpoints that belong to a module
    
    Args:
        module_key: Module key (e.g., "creditRequests")
        
    Returns:
        List of endpoint prefixes that belong to this module
    """
    endpoints = []
    for endpoint, mapped_module in ENDPOINT_TO_MODULE_KEY.items():
        if mapped_module == module_key:
            endpoints.append(endpoint)
    return endpoints
