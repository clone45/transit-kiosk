from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ApiKey:
    id: int
    name: str  # e.g., "Kiosk_Downtown_01", "Testing_Environment"
    key_hash: str  # Hashed version of the API key
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    usage_count: int = 0

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key_hash': self.key_hash,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'last_used_at': self.last_used_at,
            'usage_count': self.usage_count
        }

    def to_public_dict(self):
        """Return API key data without sensitive fields"""
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'last_used_at': self.last_used_at,
            'usage_count': self.usage_count
        }