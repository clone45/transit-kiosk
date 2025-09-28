#!/usr/bin/env python3
"""
Delete a trip by trip ID for the test transit card.

Usage:
    python delete_trip.py <trip_id>

Example:
    python delete_trip.py 5
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

def delete_trip(uuid, trip_id):
    """Delete a trip by ID for a card with the given UUID."""
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

    # Check if trip exists and belongs to this card
    cursor.execute("""
        SELECT t.id, s1.name, s2.name, t.status
        FROM trips t
        LEFT JOIN stations s1 ON t.source_station_id = s1.id
        LEFT JOIN stations s2 ON t.destination_station_id = s2.id
        WHERE t.id = ? AND t.card_id = ?
    """, (trip_id, card_id))

    trip_result = cursor.fetchone()

    if not trip_result:
        print(f"Error: Trip ID {trip_id} not found for this card")
        conn.close()
        sys.exit(1)

    trip_id_db, source, destination, status = trip_result

    # Delete the trip
    cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
    conn.commit()

    destination_display = destination if destination else "N/A"
    print(f"Deleted trip {trip_id}:")
    print(f"  From: {source}")
    print(f"  To: {destination_display}")
    print(f"  Status: {status}")

    conn.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python delete_trip.py <trip_id>")
        print("Example: python delete_trip.py 5")
        sys.exit(1)

    try:
        trip_id = int(sys.argv[1])
    except ValueError:
        print(f"Error: Invalid trip ID: {sys.argv[1]}")
        sys.exit(1)

    uuid = get_card_uuid_from_env()
    delete_trip(uuid, trip_id)

if __name__ == "__main__":
    main()