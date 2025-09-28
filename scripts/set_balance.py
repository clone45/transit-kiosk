#!/usr/bin/env python3
"""
Set the balance of the test transit card.

Usage:
    python set_balance.py <amount>

Example:
    python set_balance.py 0      # Set balance to $0
    python set_balance.py 25.50  # Set balance to $25.50
"""

import sys
import sqlite3
from pathlib import Path
from decimal import Decimal

# Get paths
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
DB_PATH = BACKEND_DIR / "transit_kiosk.db"
ENV_PATH = FRONTEND_DIR / ".env"

def get_card_uuid_from_env():
    """Read the test card UUID from frontend .env file."""
    if not ENV_PATH.exists():
        print(f"Error: .env file not found at {ENV_PATH}")
        sys.exit(1)

    with open(ENV_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('VITE_TEST_CARD_UUID='):
                uuid = line.split('=', 1)[1].strip()
                if uuid:
                    return uuid

    print("Error: VITE_TEST_CARD_UUID not found or empty in .env file")
    sys.exit(1)

def set_balance(uuid, balance):
    """Set the balance for a card with the given UUID."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run 'python backend/seed.py --tag dev' to create the database")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if card exists
    cursor.execute("SELECT id, balance FROM transit_cards WHERE uuid = ?", (uuid,))
    result = cursor.fetchone()

    if not result:
        print(f"Error: Card with UUID {uuid} not found in database")
        conn.close()
        sys.exit(1)

    card_id, old_balance = result

    # Update balance
    cursor.execute("UPDATE transit_cards SET balance = ? WHERE uuid = ?", (float(balance), uuid))
    conn.commit()
    conn.close()

    print(f"Card {uuid}")
    print(f"  Old balance: ${float(old_balance):.2f}")
    print(f"  New balance: ${float(balance):.2f}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python set_balance.py <amount>")
        print("Example: python set_balance.py 25.50")
        sys.exit(1)

    try:
        balance = Decimal(sys.argv[1])
        if balance < 0:
            print("Error: Balance cannot be negative")
            sys.exit(1)
    except (ValueError, ArithmeticError):
        print(f"Error: Invalid balance amount: {sys.argv[1]}")
        sys.exit(1)

    uuid = get_card_uuid_from_env()
    set_balance(uuid, balance)

if __name__ == "__main__":
    main()