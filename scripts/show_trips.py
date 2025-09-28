#!/usr/bin/env python3
"""
Show all trips for the test transit card.

Usage:
    python show_trips.py
"""

import sys
import sqlite3
from pathlib import Path

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

def show_trips(uuid):
    """Show all trips for a card with the given UUID."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        print("Run 'python backend/seed.py --tag dev' to create the database")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get card ID
    cursor.execute("SELECT id FROM transit_cards WHERE uuid = ?", (uuid,))
    result = cursor.fetchone()

    if not result:
        print(f"Error: Card with UUID {uuid} not found in database")
        conn.close()
        sys.exit(1)

    card_id = result[0]

    # Get trips with station names
    cursor.execute("""
        SELECT
            t.id,
            t.card_id,
            t.start_time,
            t.completion_time,
            s1.name as source_station,
            s2.name as destination_station,
            t.cost,
            t.status
        FROM trips t
        LEFT JOIN stations s1 ON t.source_station_id = s1.id
        LEFT JOIN stations s2 ON t.destination_station_id = s2.id
        WHERE t.card_id = ?
        ORDER BY t.start_time DESC
    """, (card_id,))

    trips = cursor.fetchall()

    print("=" * 110)
    print(f"TRIPS FOR CARD {uuid}")
    print("=" * 110)

    if not trips:
        print("No trips found")
    else:
        print(f"{'ID':<5} {'Card':<6} {'Start':<14} {'From':<20} {'To':<20} {'Cost':<8} {'Status':<10}")
        print("-" * 110)
        for trip_id, trip_card_id, start_time, completion_time, source, destination, cost, status in trips:
            destination_display = destination if destination else "N/A"
            start_concise = start_time[:16] if len(start_time) >= 16 else start_time
            print(f"{trip_id:<5} {trip_card_id:<6} {start_concise:<14} {source:<20} {destination_display:<20} ${float(cost):<7.2f} {status:<10}")

    print("=" * 110)
    print(f"Total trips: {len(trips)}")
    print("=" * 110)

    conn.close()

def main():
    uuid = get_card_uuid_from_env()
    show_trips(uuid)

if __name__ == "__main__":
    main()