from database import SessionLocal
from models import Chapter

from ai_chapter_detector import detect_chapters


def save_chapters(book_id, text):

    lines = text.splitlines()

    print(f"Total lines: {len(lines)}")

    # Ask AI to find chapter beginnings
    detected_chapters = detect_chapters(lines)

    print(
        f"AI detected {len(detected_chapters)} chapters"
    )

    if not detected_chapters:
        return []

    db = SessionLocal()

    try:

        # If this book was processed before,
        # remove its old chapter data.
        db.query(Chapter).filter(
            Chapter.book_id == book_id
        ).delete()

        saved_chapters = []

        for index, detected in enumerate(
            detected_chapters
        ):

            # Start of this chapter
            start_line = detected["line_number"]

            # End of this chapter
            if index + 1 < len(detected_chapters):

                end_line = (
                    detected_chapters[index + 1]["line_number"]
                    - 1
                )

            else:

                end_line = len(lines) - 1

            # Extract the ORIGINAL book text
            content = "\n".join(
                lines[start_line:end_line + 1]
            ).strip()

            chapter = Chapter(
                book_id=book_id,

                chapter_number=detected[
                    "chapter_number"
                ],

                title=detected.get(
                    "title",
                    ""
                ),

                content=content,

                start_line=start_line,

                end_line=end_line
            )

            db.add(chapter)

            saved_chapters.append(chapter)

        db.commit()

        for chapter in saved_chapters:
            db.refresh(chapter)

        return saved_chapters

    finally:

        db.close()
