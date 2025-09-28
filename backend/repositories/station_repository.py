import sqlite3
from typing import List, Optional
from repositories.base import BaseRepository
from models.station import Station


class StationRepository(BaseRepository):
    """Repository for station database operations."""

    def _init_db(self):
        """Initialize the database with stations table."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            conn.commit()

            # Seed with some default stations if table is empty
            self._seed_default_stations(conn)

    def _seed_default_stations(self, conn: sqlite3.Connection):
        """Seed default stations if the table is empty."""
        cursor = conn.execute("SELECT COUNT(*) FROM stations")
        count = cursor.fetchone()[0]

        if count == 0:
            default_stations = [
                "Central Station",
                "Union Square",
                "Airport Terminal",
                "Downtown",
                "University",
                "Stadium",
                "Harbor Point",
                "Tech Center"
            ]
            for station_name in default_stations:
                conn.execute("INSERT INTO stations (name) VALUES (?)", (station_name,))
            conn.commit()

    def create(self, name: str) -> Station:
        """Create a new station."""
        query = "INSERT INTO stations (name) VALUES (?)"
        station_id = self._execute_insert(query, (name,))
        return self.get_by_id(station_id)

    def get_by_id(self, station_id: int) -> Optional[Station]:
        """Get a station by ID."""
        query = "SELECT * FROM stations WHERE id = ?"
        rows = self._execute_query(query, (station_id,))

        if rows:
            return self._row_to_station(rows[0])
        return None

    def get_all(self) -> List[Station]:
        """Get all stations."""
        query = "SELECT * FROM stations ORDER BY name"
        rows = self._execute_query(query)
        return [self._row_to_station(row) for row in rows]

    def update(self, station_id: int, name: str) -> Optional[Station]:
        """Update a station's name."""
        query = "UPDATE stations SET name = ? WHERE id = ?"
        affected = self._execute_update(query, (name, station_id))

        if affected > 0:
            return self.get_by_id(station_id)
        return None

    def delete(self, station_id: int) -> bool:
        """Delete a station."""
        query = "DELETE FROM stations WHERE id = ?"
        affected = self._execute_update(query, (station_id,))
        return affected > 0

    def _row_to_station(self, row: sqlite3.Row) -> Station:
        """Convert a database row to Station object."""
        return Station(
            id=row['id'],
            name=row['name']
        )