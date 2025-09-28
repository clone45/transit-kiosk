from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal
import uuid


@dataclass
class TransitCard:
    """Transit card model representing a single transit card."""
    id: Optional[int] = None
    uuid: Optional[str] = None
    balance: Decimal = Decimal('0.00')
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'balance': float(self.balance),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'usage_count': self.usage_count
        }

    def has_sufficient_balance(self, amount: Decimal) -> bool:
        """Check if card has sufficient balance for a transaction."""
        return self.balance >= amount

    def format_balance(self) -> str:
        """Return formatted balance as currency string."""
        return f"${self.balance:.2f}"