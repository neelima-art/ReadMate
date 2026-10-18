from book_processor import extract_book_text
from chapter_processor import save_chapters


file_path = "uploads/The Lost World - Arthur Conan Doyle.pdf"

book_id = "the-lost-world"


print("\nExtracting book...\n")

text = extract_book_text(file_path)

print(
    "Extracted characters:",
    len(text)
)


print("\nSaving chapters...\n")


chapters = save_chapters(
    book_id,
    text
)


print("\n========== SAVED CHAPTERS ==========\n")


for chapter in chapters:

    print(
        f"Chapter {chapter.chapter_number}"
        f" | {chapter.title}"
        f" | lines {chapter.start_line}"
        f"- {chapter.end_line}"
    )


print(
    "\nTotal chapters saved:",
    len(chapters)
)
