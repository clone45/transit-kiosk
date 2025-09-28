import sqlite3
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from repositories.base import BaseRepository
from models.transit_card import TransitCard


class TransitCardRepository(BaseRepository):
    """Repository for transit card database operations."""

    def _init_db(self):
        """Initialize the database with transit_cards table."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transit_cards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT UNIQUE NOT NULL,
                    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_used_at TIMESTAMP,
                    usage_count INTEGER NOT NULL DEFAULT 0
                )
            ''')
            conn.commit()

    def create(self, balance: Decimal = Decimal('0.00'), card_uuid: Optional[str] = None) -> TransitCard:
        """Create a new transit card with initial balance and optional UUID."""
        if card_uuid is None:
            card_uuid = str(uuid.uuid4())
        query = "INSERT INTO transit_cards (uuid, balance, created_at) VALUES (?, ?, ?)"
        params = (card_uuid, float(balance), datetime.now())
        card_id = self._execute_insert(query, params)
        return self.get_by_id(card_id)

    def get_by_id(self, card_id: int) -> Optional[TransitCard]:
        """Get a transit card by ID."""
        query = "SELECT * FROM transit_cards WHERE id = ?"
        rows = self._execute_query(query, (card_id,))

        if rows:
            return self._row_to_card(rows[0])
        return None

    def get_all(self) -> List[TransitCard]:
        """Get all transit cards."""
        query = "SELECT * FROM transit_cards ORDER BY id DESC"
        rows = self._execute_query(query)
        return [self._row_to_card(row) for row in rows]

    def update_balance(self, card_id: int, new_balance: Decimal) -> Optional[TransitCard]:
        """Update card balance."""
        query = "UPDATE transit_cards SET balance = ? WHERE id = ?"
        affected = self._execute_update(query, (float(new_balance), card_id))

        if affected > 0:
            return self.get_by_id(card_id)
        return None

    def record_usage(self, card_id: int, fare: Decimal) -> Optional[TransitCard]:
        """Record a card usage - deduct fare and update usage stats."""
        card = self.get_by_id(card_id)
        if not card:
            return None

        if not card.has_sufficient_balance(fare):
            raise ValueError("Insufficient balance")

        new_balance = card.balance - fare
        query = """UPDATE transit_cards
                   SET balance = ?,
                       last_used_at = ?,
                       usage_count = usage_count + 1
                   WHERE id = ?"""
        params = (float(new_balance), datetime.now(), card_id)
        affected = self._execute_update(query, params)

        if affected > 0:
            return self.get_by_id(card_id)
        return None

    def add_funds(self, card_id: int, amount: Decimal) -> Optional[TransitCard]:
        """Add funds to a transit card."""
        card = self.get_by_id(card_id)
        if not card:
            return None

        new_balance = card.balance + amount
        return self.update_balance(card_id, new_balance)

    def get_active_cards(self, days: int = 30) -> List[TransitCard]:
        """Get cards that have been used within the last N days."""
        query = """SELECT * FROM transit_cards
                   WHERE last_used_at > datetime('now', ? || ' days')
                   ORDER BY last_used_at DESC"""
        rows = self._execute_query(query, (f'-{days}',))
        return [self._row_to_card(row) for row in rows]

    def get_cards_by_balance_range(self, min_balance: Decimal, max_balance: Decimal) -> List[TransitCard]:
        """Get cards within a specific balance range."""
        query = "SELECT * FROM transit_cards WHERE balance >= ? AND balance <= ? ORDER BY balance DESC"
        rows = self._execute_query(query, (float(min_balance), float(max_balance)))
        return [self._row_to_card(row) for row in rows]

    def get_by_uuid(self, card_uuid: str) -> Optional[TransitCard]:
        """Get a transit card by UUID."""
        query = "SELECT * FROM transit_cards WHERE uuid = ?"
        rows = self._execute_query(query, (card_uuid,))

        if rows:
            return self._row_to_card(rows[0])
        return None

    def _row_to_card(self, row: sqlite3.Row) -> TransitCard:
        """Convert a database row to TransitCard object."""
        return TransitCard(
            id=row['id'],
            uuid=row['uuid'],
            balance=Decimal(str(row['balance'])),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
            last_used_at=datetime.fromisoformat(row['last_used_at']) if row['last_used_at'] else None,
            usage_count=row['usage_count']
        )