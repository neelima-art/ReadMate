import sqlite3


conn = sqlite3.connect("readmate.db")

cursor = conn.cursor()


old_id = "the-lost-world"

new_id = "the-lost-world---arthur-conan-doyle"


cursor.execute(
    """
    UPDATE chapters
    SET book_id = ?
    WHERE book_id = ?
    """,
    (new_id, old_id)
)


print(
    "Chapters updated:",
    cursor.rowcount
)


conn.commit()

conn.close()


print("Done!")

