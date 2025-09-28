import argparse
import sqlite3
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parent
DB_PATH = ROOT / "transit_kiosk.db"

def connect():
    cn = sqlite3.connect(DB_PATH)
    cn.execute("PRAGMA foreign_keys=ON;")
    return cn

def ensure_meta(cn):
    cn.execute("""CREATE TABLE IF NOT EXISTS _migrations(
        name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)""")

def run_migrations(cn):
    ensure_meta(cn)
    migrations_folder = ROOT / "db" / "migrations"

    if not migrations_folder.exists():
        print(f"Error: Migrations folder not found: {migrations_folder}")
        return

    applied = {r[0] for r in cn.execute("SELECT name FROM _migrations")}
    sql_files = sorted(migrations_folder.glob("*.sql"))

    if not sql_files:
        print("No migration files found.")
        return

    for path in sql_files:
        if path.name in applied:
            print(f"  [OK] {path.name} (already applied)")
            continue

        with cn:
            sql = path.read_text(encoding="utf-8")
            cn.executescript(sql)
            cn.execute("INSERT INTO _migrations(name, applied_at) VALUES (?,?)",
                      (path.name, time.strftime("%Y-%m-%d %H:%M:%S")))
            print(f"  [OK] {path.name} (applied)")

def cmd_migrate(_):
    cn = connect()
    print("Running migrations...")
    run_migrations(cn)
    print("[OK] Migrations up to date")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database migration utility")
    parser.set_defaults(func=cmd_migrate)
    args = parser.parse_args()
    args.func(args)