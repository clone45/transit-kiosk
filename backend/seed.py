import argparse
import sqlite3
import pathlib
import time
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
DB_PATH = ROOT / "transit_kiosk.db"

def connect():
    cn = sqlite3.connect(DB_PATH)
    cn.execute("PRAGMA foreign_keys=ON;")
    return cn

def run_migrations():
    """Run migrations before seeding"""
    print("Checking migrations...")
    result = subprocess.run([sys.executable, str(ROOT / "migrate.py")],
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Migration failed: {result.stderr}")
        sys.exit(1)
    print(result.stdout)

def ensure_meta(cn):
    cn.execute("""CREATE TABLE IF NOT EXISTS _seed_runs(
        name TEXT PRIMARY KEY, applied_at TEXT NOT NULL, tag TEXT NOT NULL)""")

def run_folder(cn, folder, tag):
    ensure_meta(cn)
    applied = {r[0] for r in cn.execute("SELECT name FROM _seed_runs")}

    if not folder.exists():
        print(f"Seed folder not found: {folder}")
        return

    sql_files = sorted(folder.glob("*.sql"))
    if not sql_files:
        print(f"No seed files found in {folder}")
        return

    for path in sql_files:
        if path.name in applied:
            print(f"  [OK] {path.name} (already applied)")
            continue

        with cn:
            sql = path.read_text(encoding="utf-8")
            cn.executescript(sql)
            cn.execute("INSERT INTO _seed_runs(name, applied_at, tag) VALUES (?,?,?)",
                      (path.name, time.strftime("%Y-%m-%d %H:%M:%S"), tag))
            print(f"  [OK] {path.name} (applied)")

def cmd_seed(args):
    # Run migrations first
    run_migrations()

    cn = connect()
    tag = args.tag
    folder = ROOT / "db" / "seeds" / tag

    if not folder.exists():
        print(f"Error: No such seed tag: {tag}")
        print(f"Available tags: baseline, dev")
        return

    print(f"Running '{tag}' seeds...")
    run_folder(cn, folder, tag=tag)
    print(f"[OK] All '{tag}' seeds applied successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database seeding utility")
    parser.add_argument("--tag", choices=["baseline", "dev"], required=True,
                       help="Seed tag to apply (baseline=required data, dev=test data)")
    args = parser.parse_args()
    cmd_seed(args)