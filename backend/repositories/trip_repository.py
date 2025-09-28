import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from repositories.base import BaseRepository
from models.trip import Trip, TripStatus


class TripRepository(BaseRepository):
    """Repository for trip database operations."""

    def _init_db(self):
        """Initialize the database with trips table."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    completion_time TIMESTAMP,
                    source_station_id INTEGER NOT NULL,
                    destination_station_id INTEGER,
                    cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                    status TEXT NOT NULL DEFAULT 'active',
                    FOREIGN KEY (card_id) REFERENCES transit_cards (id),
                    FOREIGN KEY (source_station_id) REFERENCES stations (id),
                    FOREIGN KEY (destination_station_id) REFERENCES stations (id)
                )
            ''')
            conn.commit()

    def create(self, card_id: int, source_station_id: int, cost: Decimal = Decimal('0.00')) -> Trip:
        """Create a new active trip."""
        query = """INSERT INTO trips (card_id, start_time, source_station_id, cost, status)
                   VALUES (?, ?, ?, ?, ?)"""
        params = (card_id, datetime.now(), source_station_id, float(cost), TripStatus.ACTIVE.value)
        trip_id = self._execute_insert(query, params)
        return self.get_by_id(trip_id)

    def get_by_id(self, trip_id: int) -> Optional[Trip]:
        """Get a trip by ID."""
        query = "SELECT * FROM trips WHERE id = ?"
        rows = self._execute_query(query, (trip_id,))

        if rows:
            return self._row_to_trip(rows[0])
        return None

    def get_all(self) -> List[Trip]:
        """Get all trips."""
        query = "SELECT * FROM trips ORDER BY start_time DESC"
        rows = self._execute_query(query)
        return [self._row_to_trip(row) for row in rows]

    def get_by_card_id(self, card_id: int) -> List[Trip]:
        """Get all trips for a specific card."""
        query = "SELECT * FROM trips WHERE card_id = ? ORDER BY start_time DESC"
        rows = self._execute_query(query, (card_id,))
        return [self._row_to_trip(row) for row in rows]

    def get_active_trip_by_card(self, card_id: int) -> Optional[Trip]:
        """Get active trip for a card (if any)."""
        query = "SELECT * FROM trips WHERE card_id = ? AND status = ? ORDER BY start_time DESC LIMIT 1"
        rows = self._execute_query(query, (card_id, TripStatus.ACTIVE.value))

        if rows:
            return self._row_to_trip(rows[0])
        return None

    def complete_trip(self, trip_id: int, destination_station_id: int, final_cost: Decimal = None) -> Optional[Trip]:
        """Complete an active trip."""
        trip = self.get_by_id(trip_id)
        if not trip or not trip.is_active():
            return None

        # Use existing cost if no new cost provided
        cost_to_use = final_cost if final_cost is not None else trip.cost

        query = """UPDATE trips
                   SET completion_time = ?, destination_station_id = ?, cost = ?, status = ?
                   WHERE id = ?"""
        params = (datetime.now(), destination_station_id, float(cost_to_use), TripStatus.COMPLETED.value, trip_id)
        affected = self._execute_update(query, params)

        if affected > 0:
            return self.get_by_id(trip_id)
        return None

    def cancel_trip(self, trip_id: int) -> Optional[Trip]:
        """Cancel an active trip."""
        query = "UPDATE trips SET status = ? WHERE id = ? AND status = ?"
        params = (TripStatus.CANCELLED.value, trip_id, TripStatus.ACTIVE.value)
        affected = self._execute_update(query, params)

        if affected > 0:
            return self.get_by_id(trip_id)
        return None

    def get_trips_by_station(self, station_id: int, as_source: bool = True) -> List[Trip]:
        """Get trips by source or destination station."""
        if as_source:
            query = "SELECT * FROM trips WHERE source_station_id = ? ORDER BY start_time DESC"
        else:
            query = "SELECT * FROM trips WHERE destination_station_id = ? ORDER BY start_time DESC"

        rows = self._execute_query(query, (station_id,))
        return [self._row_to_trip(row) for row in rows]

    def get_trips_by_status(self, status: TripStatus) -> List[Trip]:
        """Get trips by status."""
        query = "SELECT * FROM trips WHERE status = ? ORDER BY start_time DESC"
        rows = self._execute_query(query, (status.value,))
        return [self._row_to_trip(row) for row in rows]

    def get_trips_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Trip]:
        """Get trips within a date range."""
        query = "SELECT * FROM trips WHERE start_time BETWEEN ? AND ? ORDER BY start_time DESC"
        rows = self._execute_query(query, (start_date, end_date))
        return [self._row_to_trip(row) for row in rows]

    def _row_to_trip(self, row: sqlite3.Row) -> Trip:
        """Convert a database row to Trip object."""
        return Trip(
            id=row['id'],
            card_id=row['card_id'],
            start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
            completion_time=datetime.fromisoformat(row['completion_time']) if row['completion_time'] else None,
            source_station_id=row['source_station_id'],
            destination_station_id=row['destination_station_id'],
            cost=Decimal(str(row['cost'])),
            status=TripStatus(row['status'])
        )