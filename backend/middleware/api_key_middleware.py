from fastapi import HTTPException, Depends, status, Header
from typing import Optional
from repositories.api_key_repository import ApiKeyRepository
from models.api_key import ApiKey

# Initialize repository
api_key_db = ApiKeyRepository("transit_kiosk.db")

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> ApiKey:
    """
    Dependency to verify API key from X-API-Key header.
    Use this to protect routes that require API key authentication.

    Usage in routes:
    @router.get("/protected-route")
    async def protected_route(api_key: ApiKey = Depends(verify_api_key)):
        return {"message": f"Authenticated with key: {api_key.name}"}
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Verify the API key
    api_key_record = api_key_db.get_by_key(x_api_key)
    if not api_key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not api_key_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is inactive",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Update usage statistics
    api_key_db.update_usage(api_key_record.id)

    return api_key_record

async def verify_api_key_optional(x_api_key: Optional[str] = Header(None)) -> Optional[ApiKey]:
    """
    Dependency to optionally verify API key from X-API-Key header.
    Use this for routes that can work with or without authentication.
    """
    if not x_api_key:
        return None

    try:
        return await verify_api_key(x_api_key)
    except HTTPException:
        return None