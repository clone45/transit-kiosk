import sqlite3
from decimal import Decimal
from typing import List, Optional
from repositories.base import BaseRepository
from models.pricing import Pricing


class PricingRepository(BaseRepository):
    """Repository for pricing database operations."""

    def _init_db(self):
        """Initialize the database with pricing table."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pricing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_a_id INTEGER NOT NULL,
                    station_b_id INTEGER NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    FOREIGN KEY (station_a_id) REFERENCES stations (id),
                    FOREIGN KEY (station_b_id) REFERENCES stations (id),
                    UNIQUE(station_a_id, station_b_id)
                )
            ''')
            conn.commit()

            # Seed with default pricing if table is empty
            self._seed_default_pricing(conn)

    def _seed_default_pricing(self, conn: sqlite3.Connection):
        """Seed default pricing if the table is empty."""
        cursor = conn.execute("SELECT COUNT(*) FROM pricing")
        count = cursor.fetchone()[0]

        if count == 0:
            # Get all stations first
            stations = conn.execute("SELECT id FROM stations ORDER BY id").fetchall()

            # Fixed prices for different routes (just examples)
            default_prices = [
                3.25, 4.50, 2.75, 5.00, 3.75, 4.25,
                3.50, 4.00, 2.50, 5.50, 3.00, 4.75,
                3.25, 2.25, 4.50, 3.75, 5.25, 2.75,
                4.00, 3.50, 4.25, 2.50, 5.00, 3.25,
                4.75, 3.75, 2.25
            ]

            # Create pricing for all station pairs with fixed prices
            price_index = 0
            for i, station_a in enumerate(stations):
                for station_b in stations[i+1:]:  # Only create one direction (A->B, not B->A)
                    # Use fixed price from the list, cycling through if needed
                    price = default_prices[price_index % len(default_prices)]
                    price_index += 1

                    conn.execute(
                        "INSERT INTO pricing (station_a_id, station_b_id, price) VALUES (?, ?, ?)",
                        (station_a[0], station_b[0], price)
                    )
            conn.commit()

    def create(self, station_a_id: int, station_b_id: int, price: Decimal) -> Pricing:
        """Create a new pricing entry."""
        # Ensure consistent ordering (lower ID first)
        if station_a_id > station_b_id:
            station_a_id, station_b_id = station_b_id, station_a_id

        query = "INSERT INTO pricing (station_a_id, station_b_id, price) VALUES (?, ?, ?)"
        pricing_id = self._execute_insert(query, (station_a_id, station_b_id, float(price)))
        return self.get_by_id(pricing_id)

    def get_by_id(self, pricing_id: int) -> Optional[Pricing]:
        """Get a pricing entry by ID."""
        query = "SELECT * FROM pricing WHERE id = ?"
        rows = self._execute_query(query, (pricing_id,))

        if rows:
            return self._row_to_pricing(rows[0])
        return None

    def get_all(self) -> List[Pricing]:
        """Get all pricing entries."""
        query = "SELECT * FROM pricing ORDER BY station_a_id, station_b_id"
        rows = self._execute_query(query)
        return [self._row_to_pricing(row) for row in rows]

    def get_price(self, station_a_id: int, station_b_id: int) -> Optional[Decimal]:
        """Get price between two stations."""
        # Ensure consistent ordering (lower ID first)
        if station_a_id > station_b_id:
            station_a_id, station_b_id = station_b_id, station_a_id

        query = "SELECT price FROM pricing WHERE station_a_id = ? AND station_b_id = ?"
        rows = self._execute_query(query, (station_a_id, station_b_id))

        if rows:
            return Decimal(str(rows[0][0]))
        return None

    def get_pricing_by_stations(self, station_a_id: int, station_b_id: int) -> Optional[Pricing]:
        """Get pricing entry between two stations."""
        # Ensure consistent ordering (lower ID first)
        if station_a_id > station_b_id:
            station_a_id, station_b_id = station_b_id, station_a_id

        query = "SELECT * FROM pricing WHERE station_a_id = ? AND station_b_id = ?"
        rows = self._execute_query(query, (station_a_id, station_b_id))

        if rows:
            return self._row_to_pricing(rows[0])
        return None

    def get_prices_for_station(self, station_id: int) -> List[Pricing]:
        """Get all pricing entries involving a specific station."""
        query = "SELECT * FROM pricing WHERE station_a_id = ? OR station_b_id = ?"
        rows = self._execute_query(query, (station_id, station_id))
        return [self._row_to_pricing(row) for row in rows]

    def update_price(self, station_a_id: int, station_b_id: int, new_price: Decimal) -> Optional[Pricing]:
        """Update price between two stations."""
        # Ensure consistent ordering (lower ID first)
        if station_a_id > station_b_id:
            station_a_id, station_b_id = station_b_id, station_a_id

        query = "UPDATE pricing SET price = ? WHERE station_a_id = ? AND station_b_id = ?"
        affected = self._execute_update(query, (float(new_price), station_a_id, station_b_id))

        if affected > 0:
            return self.get_pricing_by_stations(station_a_id, station_b_id)
        return None

    def delete_pricing(self, station_a_id: int, station_b_id: int) -> bool:
        """Delete pricing between two stations."""
        # Ensure consistent ordering (lower ID first)
        if station_a_id > station_b_id:
            station_a_id, station_b_id = station_b_id, station_a_id

        query = "DELETE FROM pricing WHERE station_a_id = ? AND station_b_id = ?"
        affected = self._execute_update(query, (station_a_id, station_b_id))
        return affected > 0

    def get_highest_price(self) -> Optional[Pricing]:
        """Get the pricing entry with the highest price."""
        query = "SELECT * FROM pricing ORDER BY price DESC LIMIT 1"
        rows = self._execute_query(query)

        if rows:
            return self._row_to_pricing(rows[0])
        return None

    def get_lowest_price(self) -> Optional[Pricing]:
        """Get the pricing entry with the lowest price."""
        query = "SELECT * FROM pricing ORDER BY price ASC LIMIT 1"
        rows = self._execute_query(query)

        if rows:
            return self._row_to_pricing(rows[0])
        return None

    def get_average_price(self) -> Decimal:
        """Get the average price across all routes."""
        query = "SELECT AVG(price) FROM pricing"
        rows = self._execute_query(query)
        return Decimal(str(rows[0][0])) if rows and rows[0][0] else Decimal('0.00')

    def _row_to_pricing(self, row: sqlite3.Row) -> Pricing:
        """Convert a database row to Pricing object."""
        return Pricing(
            id=row['id'],
            station_a_id=row['station_a_id'],
            station_b_id=row['station_b_id'],
            price=Decimal(str(row['price']))
        )