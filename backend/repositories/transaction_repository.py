import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from repositories.base import BaseRepository
from models.transaction import Transaction


class TransactionRepository(BaseRepository):
    """Repository for transaction database operations."""

    def _init_db(self):
        """Initialize the database with transactions table."""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    card_id INTEGER NOT NULL,
                    transaction_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    amount DECIMAL(10, 2) NOT NULL,
                    previous_balance DECIMAL(10, 2) NOT NULL,
                    new_balance DECIMAL(10, 2) NOT NULL,
                    station_id INTEGER,
                    FOREIGN KEY (card_id) REFERENCES transit_cards (id),
                    FOREIGN KEY (station_id) REFERENCES stations (id)
                )
            ''')
            conn.commit()

    def create(self, card_id: int, amount: Decimal, previous_balance: Decimal,
               new_balance: Decimal, station_id: Optional[int] = None) -> Transaction:
        """Create a new transaction record."""
        query = """INSERT INTO transactions (card_id, transaction_time, amount, previous_balance, new_balance, station_id)
                   VALUES (?, ?, ?, ?, ?, ?)"""
        params = (card_id, datetime.now(), float(amount), float(previous_balance),
                 float(new_balance), station_id)
        transaction_id = self._execute_insert(query, params)
        return self.get_by_id(transaction_id)

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get a transaction by ID."""
        query = "SELECT * FROM transactions WHERE id = ?"
        rows = self._execute_query(query, (transaction_id,))

        if rows:
            return self._row_to_transaction(rows[0])
        return None

    def get_all(self) -> List[Transaction]:
        """Get all transactions."""
        query = "SELECT * FROM transactions ORDER BY transaction_time DESC"
        rows = self._execute_query(query)
        return [self._row_to_transaction(row) for row in rows]

    def get_by_card_id(self, card_id: int) -> List[Transaction]:
        """Get all transactions for a specific card."""
        query = "SELECT * FROM transactions WHERE card_id = ? ORDER BY transaction_time DESC"
        rows = self._execute_query(query, (card_id,))
        return [self._row_to_transaction(row) for row in rows]

    def get_by_station_id(self, station_id: int) -> List[Transaction]:
        """Get all transactions for a specific station."""
        query = "SELECT * FROM transactions WHERE station_id = ? ORDER BY transaction_time DESC"
        rows = self._execute_query(query, (station_id,))
        return [self._row_to_transaction(row) for row in rows]

    def get_credits_by_card(self, card_id: int) -> List[Transaction]:
        """Get all credit transactions for a card."""
        query = "SELECT * FROM transactions WHERE card_id = ? AND amount > 0 ORDER BY transaction_time DESC"
        rows = self._execute_query(query, (card_id,))
        return [self._row_to_transaction(row) for row in rows]

    def get_debits_by_card(self, card_id: int) -> List[Transaction]:
        """Get all debit transactions for a card."""
        query = "SELECT * FROM transactions WHERE card_id = ? AND amount < 0 ORDER BY transaction_time DESC"
        rows = self._execute_query(query, (card_id,))
        return [self._row_to_transaction(row) for row in rows]

    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get transactions within a date range."""
        query = "SELECT * FROM transactions WHERE transaction_time BETWEEN ? AND ? ORDER BY transaction_time DESC"
        rows = self._execute_query(query, (start_date, end_date))
        return [self._row_to_transaction(row) for row in rows]

    def get_card_transactions_by_date_range(self, card_id: int, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get transactions for a card within a date range."""
        query = """SELECT * FROM transactions
                   WHERE card_id = ? AND transaction_time BETWEEN ? AND ?
                   ORDER BY transaction_time DESC"""
        rows = self._execute_query(query, (card_id, start_date, end_date))
        return [self._row_to_transaction(row) for row in rows]

    def get_total_spent_by_card(self, card_id: int) -> Decimal:
        """Get total amount spent (debits) by a card."""
        query = "SELECT COALESCE(SUM(ABS(amount)), 0) FROM transactions WHERE card_id = ? AND amount < 0"
        rows = self._execute_query(query, (card_id,))
        return Decimal(str(rows[0][0])) if rows else Decimal('0.00')

    def get_total_added_by_card(self, card_id: int) -> Decimal:
        """Get total amount added (credits) to a card."""
        query = "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE card_id = ? AND amount > 0"
        rows = self._execute_query(query, (card_id,))
        return Decimal(str(rows[0][0])) if rows else Decimal('0.00')

    def get_latest_transaction_by_card(self, card_id: int) -> Optional[Transaction]:
        """Get the most recent transaction for a card."""
        query = "SELECT * FROM transactions WHERE card_id = ? ORDER BY transaction_time DESC LIMIT 1"
        rows = self._execute_query(query, (card_id,))

        if rows:
            return self._row_to_transaction(rows[0])
        return None

    def get_station_revenue(self, station_id: int) -> Decimal:
        """Get total revenue (debits) for a station."""
        query = "SELECT COALESCE(SUM(ABS(amount)), 0) FROM transactions WHERE station_id = ? AND amount < 0"
        rows = self._execute_query(query, (station_id,))
        return Decimal(str(rows[0][0])) if rows else Decimal('0.00')

    def _row_to_transaction(self, row: sqlite3.Row) -> Transaction:
        """Convert a database row to Transaction object."""
        return Transaction(
            id=row['id'],
            card_id=row['card_id'],
            transaction_time=datetime.fromisoformat(row['transaction_time']) if row['transaction_time'] else None,
            amount=Decimal(str(row['amount'])),
            previous_balance=Decimal(str(row['previous_balance'])),
            new_balance=Decimal(str(row['new_balance'])),
            station_id=row['station_id']
        )