from dataclasses import dataclass
from typing import Optional


@dataclass
class Station:
    """Station model representing a transit station."""
    id: Optional[int] = None
    name: str = ""

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name
        }