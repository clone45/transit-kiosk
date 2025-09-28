#!/usr/bin/env python3
"""
Show the balance and details of the test transit card.

Usage:
    python show_balance.py
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

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

def show_balance(uuid):
    """Show the balance and details for a card with the given UUID."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run 'python backend/seed.py --tag dev' to create the database")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get card details
    cursor.execute("""
        SELECT id, uuid, balance, created_at, last_used_at, usage_count
        FROM transit_cards
        WHERE uuid = ?
    """, (uuid,))
    result = cursor.fetchone()

    if not result:
        print(f"Error: Card with UUID {uuid} not found in database")
        conn.close()
        sys.exit(1)

    card_id, uuid, balance, created_at, last_used_at, usage_count = result

    print("=" * 60)
    print("TRANSIT CARD DETAILS")
    print("=" * 60)
    print(f"Card ID:      {card_id}")
    print(f"UUID:         {uuid}")
    print(f"Balance:      ${float(balance):.2f}")
    print(f"Usage Count:  {usage_count}")
    print(f"Created:      {created_at}")
    print(f"Last Used:    {last_used_at if last_used_at else 'Never'}")
    print("=" * 60)

    conn.close()

def main():
    uuid = get_card_uuid_from_env()
    show_balance(uuid)

if __name__ == "__main__":
    main()