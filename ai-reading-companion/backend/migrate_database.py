
import sqlite3
import os

# Always use the database file in this backend folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "readmate.db")

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

try:
    # 1. Ensure the folders table exists.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Add folder_id to existing books, if it is missing.
    existing_columns = {
        column[1]
        for column in cursor.execute(
            "PRAGMA table_info(books)"
        ).fetchall()
    }

    if "folder_id" not in existing_columns:
        cursor.execute("""
            ALTER TABLE books
            ADD COLUMN folder_id INTEGER
            REFERENCES folders(id)
        """)
        print("Added books.folder_id")
    else:
        print("books.folder_id already exists")

    # 3. Preserve the existing chapter migration.
    existing_chapter_columns = {
        column[1]
        for column in cursor.execute(
            "PRAGMA table_info(chapters)"
        ).fetchall()
    }

    for column_name, column_type in [
        ("start_page", "INTEGER"),
        ("end_page", "INTEGER"),
        ("content", "TEXT"),
    ]:
        if column_name not in existing_chapter_columns:
            cursor.execute(
                f"ALTER TABLE chapters "
                f"ADD COLUMN {column_name} {column_type}"
            )
            print(f"Added chapters.{column_name}")

    # 4. Preserve the existing book_pages table.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_pages (
            id INTEGER PRIMARY KEY,
            book_id TEXT,
            page_number INTEGER,
            content TEXT
        )
    """)

    conn.commit()
    print("Database migration completed successfully.")

except Exception:
    conn.rollback()
    raise

finally:
    conn.close()
