from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum


class TripStatus(Enum):
    """Trip status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Trip:
    """Trip model representing a transit journey."""
    id: Optional[int] = None
    card_id: int = None
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    source_station_id: int = None
    destination_station_id: Optional[int] = None
    cost: Decimal = Decimal('0.00')
    status: TripStatus = TripStatus.ACTIVE

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'card_id': self.card_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'completion_time': self.completion_time.isoformat() if self.completion_time else None,
            'source_station_id': self.source_station_id,
            'destination_station_id': self.destination_station_id,
            'cost': float(self.cost),
            'status': self.status.value
        }

    def is_active(self) -> bool:
        """Check if trip is currently active."""
        return self.status == TripStatus.ACTIVE

    def is_completed(self) -> bool:
        """Check if trip is completed."""
        return self.status == TripStatus.COMPLETED

    def duration_minutes(self) -> Optional[int]:
        """Get trip duration in minutes if completed."""
        if self.start_time and self.completion_time:
            delta = self.completion_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None