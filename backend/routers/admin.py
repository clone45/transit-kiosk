from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from repositories.api_key_repository import ApiKeyRepository
from models.api_key import ApiKey

router = APIRouter()

# Initialize repository
api_key_db = ApiKeyRepository("transit_kiosk.db")

# Pydantic models for API key management
class ApiKeyCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100, description="Descriptive name for the API key")

class ApiKeyResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    usage_count: int

class ApiKeyCreateResponse(BaseModel):
    id: int
    name: str
    api_key: str  # Only returned once during creation
    is_active: bool

# Note: In a production environment, you might want additional authentication
# for these admin endpoints (like a master API key or IP whitelist)

@router.post("/api-keys", response_model=ApiKeyCreateResponse)
async def create_api_key(key_data: ApiKeyCreate):
    """Create a new API key for a kiosk or application"""
    try:
        api_key_record, actual_key = api_key_db.create(key_data.name)
        return ApiKeyCreateResponse(
            id=api_key_record.id,
            name=api_key_record.name,
            api_key=actual_key,  # Only returned here!
            is_active=api_key_record.is_active
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create API key: {str(e)}")

@router.get("/api-keys", response_model=List[ApiKeyResponse])
async def get_all_api_keys():
    """Get all API keys (without the actual key values)"""
    api_keys = api_key_db.get_all()
    return [
        ApiKeyResponse(
            id=key.id,
            name=key.name,
            is_active=key.is_active,
            usage_count=key.usage_count
        )
        for key in api_keys
    ]

@router.get("/api-keys/{key_id}", response_model=ApiKeyResponse)
async def get_api_key(key_id: int):
    """Get a specific API key by ID"""
    api_key = api_key_db.get_by_id(key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return ApiKeyResponse(
        id=api_key.id,
        name=api_key.name,
        is_active=api_key.is_active,
        usage_count=api_key.usage_count
    )

@router.post("/api-keys/{key_id}/deactivate")
async def deactivate_api_key(key_id: int):
    """Deactivate an API key"""
    success = api_key_db.deactivate_key(key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key deactivated successfully"}

@router.post("/api-keys/{key_id}/activate")
async def activate_api_key(key_id: int):
    """Reactivate an API key"""
    success = api_key_db.activate_key(key_id)
    if not success:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"message": "API key activated successfully"}

@router.get("/api-keys/{key_id}/usage")
async def get_api_key_usage(key_id: int):
    """Get usage statistics for an API key"""
    api_key = api_key_db.get_by_id(key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return {
        "key_id": api_key.id,
        "name": api_key.name,
        "usage_count": api_key.usage_count,
        "last_used_at": api_key.last_used_at,
        "created_at": api_key.created_at,
        "is_active": api_key.is_active
    }