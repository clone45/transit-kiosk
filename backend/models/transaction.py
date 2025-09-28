from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class Transaction:
    """Transaction model representing a card balance change."""
    id: Optional[int] = None
    card_id: int = None
    transaction_time: Optional[datetime] = None
    amount: Decimal = Decimal('0.00')
    previous_balance: Decimal = Decimal('0.00')
    new_balance: Decimal = Decimal('0.00')
    station_id: Optional[int] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'card_id': self.card_id,
            'transaction_time': self.transaction_time.isoformat() if self.transaction_time else None,
            'amount': float(self.amount),
            'previous_balance': float(self.previous_balance),
            'new_balance': float(self.new_balance),
            'station_id': self.station_id
        }

    def is_debit(self) -> bool:
        """Check if transaction is a debit (negative amount)."""
        return self.amount < 0

    def is_credit(self) -> bool:
        """Check if transaction is a credit (positive amount)."""
        return self.amount > 0

    def format_amount(self) -> str:
        """Return formatted amount as currency string."""
        return f"${abs(self.amount):.2f}"

    def transaction_type(self) -> str:
        """Get transaction type as string."""
        if self.is_credit():
            return "Credit" if self.station_id is None else "Refund"
        else:
            return "Debit" if self.station_id is None else "Trip Charge"