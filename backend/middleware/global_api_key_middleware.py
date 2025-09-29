from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from repositories.api_key_repository import ApiKeyRepository
import hashlib

class GlobalApiKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exempted_paths: list = None):
        super().__init__(app)
        self.api_key_db = ApiKeyRepository("transit_kiosk.db")
        # Paths that don't require API key authentication
        self.exempted_paths = exempted_paths or [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]

    def _hash_key(self, api_key: str) -> str:
        """Hash an API key for secure storage (same as repository)"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    async def dispatch(self, request: Request, call_next):
        # Check if path is exempted
        if request.url.path in self.exempted_paths:
            return await call_next(request)

        # Extract API key from header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "API key required. Include X-API-Key header."},
                headers={"WWW-Authenticate": "ApiKey"}
            )

        # Verify the API key
        api_key_record = self.api_key_db.get_by_key(api_key)
        if not api_key_record:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid API key"},
                headers={"WWW-Authenticate": "ApiKey"}
            )

        if not api_key_record.is_active:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "API key is inactive"},
                headers={"WWW-Authenticate": "ApiKey"}
            )

        # Update usage statistics
        self.api_key_db.update_usage(api_key_record.id)

        # Continue with the request
        response = await call_next(request)
        return response