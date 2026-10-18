
from database import SessionLocal
from models import (
    Book,
    ReadingProgress,
    Character,
    CharacterRelationship,
    Chapter,
    BookPage,
    ChatSession,
    ChatMessage,
    PageAnalysis,
)

DEMO_BOOK_IDS = [
    "harry-potter",
    "hobbit",
    "gatsby",
    "1984",
]

db = SessionLocal()

try:
    books = db.query(Book).filter(
        Book.book_id.in_(DEMO_BOOK_IDS)
    ).all()

    print("\nBooks selected for deletion:")
    for book in books:
        print(f"- {book.book_id}: {book.title}")

    if not books:
        print("No matching demo books found. Nothing to delete.")
    else:
        confirm = input(
            "\nType DELETE DEMO BOOKS to continue: "
        )

        if confirm != "DELETE DEMO BOOKS":
            print("Cancelled. No changes made.")
        else:
            chat_ids = [
                row[0]
                for row in db.query(ChatSession.id).filter(
                    ChatSession.book_id.in_(DEMO_BOOK_IDS)
                ).all()
            ]

            if chat_ids:
                db.query(ChatMessage).filter(
                    ChatMessage.chat_id.in_(chat_ids)
                ).delete(synchronize_session=False)

            related_models = [
                ReadingProgress,
                CharacterRelationship,
                Character,
                Chapter,
                BookPage,
                PageAnalysis,
                ChatSession,
            ]

            for model in related_models:
                count = db.query(model).filter(
                    model.book_id.in_(DEMO_BOOK_IDS)
                ).delete(synchronize_session=False)
                print(f"{model.__tablename__}: {count} rows deleted")

            count = db.query(Book).filter(
                Book.book_id.in_(DEMO_BOOK_IDS)
            ).delete(synchronize_session=False)

            print(f"books: {count} rows deleted")
            db.commit()
            print("\nCleanup completed successfully!")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
