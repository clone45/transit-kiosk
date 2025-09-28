from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class Pricing:
    """Pricing model representing fare between two stations."""
    id: Optional[int] = None
    station_a_id: int = None
    station_b_id: int = None
    price: Decimal = Decimal('0.00')

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'station_a_id': self.station_a_id,
            'station_b_id': self.station_b_id,
            'price': float(self.price)
        }

    def format_price(self) -> str:
        """Return formatted price as currency string."""
        return f"${self.price:.2f}"

    def involves_station(self, station_id: int) -> bool:
        """Check if pricing involves a specific station."""
        return station_id in (self.station_a_id, self.station_b_id)

    def get_other_station(self, station_id: int) -> Optional[int]:
        """Get the other station ID in this pricing pair."""
        if station_id == self.station_a_id:
            return self.station_b_id
        elif station_id == self.station_b_id:
            return self.station_a_id
        return None