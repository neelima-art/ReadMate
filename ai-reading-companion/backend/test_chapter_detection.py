from book_processor import extract_book_text
from ai_chapter_detector import detect_chapters


file_path = "uploads/The Lost World - Arthur Conan Doyle.pdf"


print("\nExtracting book...\n")

text = extract_book_text(file_path)

lines = text.splitlines()

print("Total lines:", len(lines))

print("\nStarting AI chapter detection...\n")

chapters = detect_chapters(lines)

print("\n========== DETECTED CHAPTERS ==========\n")

for chapter in chapters:

    print(
        f"Chapter {chapter['chapter_number']} "
        f"| line {chapter['line_number']} "
        f"| {chapter['title']}"
    )

print(
    "\nTotal chapters detected:",
    len(chapters)
)
