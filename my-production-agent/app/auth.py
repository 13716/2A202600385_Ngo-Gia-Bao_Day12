from fastapi import Header, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from .config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependency to verify API Key.
    Returns the user_id (in this simple case, we use the key or a fragment of it).
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include header: X-API-Key: <your-key>",
        )
    
    if api_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key.",
        )
    
    # Return a pseudo-user_id for rate limiting (e.g., first 8 chars or a hash)
    return "default_user"
