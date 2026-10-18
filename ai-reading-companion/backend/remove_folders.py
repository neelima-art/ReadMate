
from pathlib import Path
import sqlite3
import shutil
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "readmate.db"

if not DB_PATH.is_file():
    raise SystemExit(f"Database not found: {DB_PATH}")

backup = DB_PATH.with_name(
    f"readmate_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
)

# Back up using SQLite itself, so the backup is consistent.
with sqlite3.connect(DB_PATH) as source:
    with sqlite3.connect(backup) as destination:
        source.backup(destination)

print(f"Backup created: {backup}")

conn = sqlite3.connect(DB_PATH)

try:
    conn.execute("PRAGMA foreign_keys = ON")

    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }

    if "books" not in tables:
        raise RuntimeError("Books table missing. No changes made.")

    columns = {
        row[1]
        for row in conn.execute("PRAGMA table_info(books)")
    }

    # Check for other tables referencing folders.
    for table in tables:
        if table.startswith("sqlite_") or table == "books":
            continue

        for fk in conn.execute(
            f'PRAGMA foreign_key_list("{table}")'
        ):
            if fk[2] == "folders":
                raise RuntimeError(
                    f"Table {table} references folders. "
                    "No changes made."
                )

    if "folder_id" in columns:
        # Requires SQLite 3.35 or newer.
        conn.execute(
            "ALTER TABLE books DROP COLUMN folder_id"
        )
        print("Removed books.folder_id")

    if "folders" in tables:
        conn.execute("DROP TABLE folders")
        print("Removed folders table")

    problems = conn.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if problems:
        raise RuntimeError(
            f"Foreign key issues detected: {problems}"
        )

    conn.commit()
    print("Folder cleanup completed successfully.")

except Exception:
    conn.rollback()
    print("Cleanup failed. Backup is available at:", backup)
    raise

finally:
    conn.close()
