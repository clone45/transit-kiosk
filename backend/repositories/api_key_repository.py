import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Tuple
from repositories.base import BaseRepository
from models.api_key import ApiKey

class ApiKeyRepository(BaseRepository):

    def _init_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            key_hash TEXT UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used_at TIMESTAMP NULL,
            usage_count INTEGER DEFAULT 0
        )
        """
        self._execute_query(query)

    def _hash_key(self, api_key: str) -> str:
        """Hash an API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    def generate_api_key(self) -> str:
        """Generate a secure random API key"""
        return f"tk_{secrets.token_urlsafe(32)}"

    def create(self, name: str) -> Tuple[ApiKey, str]:
        """Create a new API key and return both the model and the actual key"""
        api_key = self.generate_api_key()
        key_hash = self._hash_key(api_key)
        created_at = datetime.now()

        query = """
        INSERT INTO api_keys (name, key_hash, created_at)
        VALUES (?, ?, ?)
        """
        key_id = self._execute_insert(query, (name, key_hash, created_at))

        api_key_model = ApiKey(
            id=key_id,
            name=name,
            key_hash=key_hash,
            is_active=True,
            created_at=created_at,
            usage_count=0
        )

        return api_key_model, api_key

    def get_by_id(self, key_id: int) -> Optional[ApiKey]:
        query = "SELECT * FROM api_keys WHERE id = ?"
        result = self._execute_query(query, (key_id,))

        if result:
            row = result[0]
            return ApiKey(
                id=row[0],
                name=row[1],
                key_hash=row[2],
                is_active=bool(row[3]),
                created_at=row[4],
                last_used_at=row[5],
                usage_count=row[6] or 0
            )
        return None

    def get_by_key(self, api_key: str) -> Optional[ApiKey]:
        """Get API key record by the actual key value"""
        key_hash = self._hash_key(api_key)
        query = "SELECT * FROM api_keys WHERE key_hash = ? AND is_active = 1"
        result = self._execute_query(query, (key_hash,))

        if result:
            row = result[0]
            return ApiKey(
                id=row[0],
                name=row[1],
                key_hash=row[2],
                is_active=bool(row[3]),
                created_at=row[4],
                last_used_at=row[5],
                usage_count=row[6] or 0
            )
        return None

    def get_all(self) -> List[ApiKey]:
        query = "SELECT * FROM api_keys ORDER BY created_at DESC"
        results = self._execute_query(query)

        return [
            ApiKey(
                id=row[0],
                name=row[1],
                key_hash=row[2],
                is_active=bool(row[3]),
                created_at=row[4],
                last_used_at=row[5],
                usage_count=row[6] or 0
            )
            for row in results
        ]

    def update_usage(self, key_id: int) -> bool:
        """Update last used timestamp and usage count"""
        query = """
        UPDATE api_keys
        SET last_used_at = ?, usage_count = usage_count + 1
        WHERE id = ?
        """
        used_at = datetime.now()

        try:
            self._execute_query(query, (used_at, key_id))
            return True
        except Exception:
            return False

    def deactivate_key(self, key_id: int) -> bool:
        """Deactivate an API key"""
        query = "UPDATE api_keys SET is_active = 0 WHERE id = ?"

        try:
            self._execute_query(query, (key_id,))
            return True
        except Exception:
            return False

    def activate_key(self, key_id: int) -> bool:
        """Reactivate an API key"""
        query = "UPDATE api_keys SET is_active = 1 WHERE id = ?"

        try:
            self._execute_query(query, (key_id,))
            return True
        except Exception:
            return False