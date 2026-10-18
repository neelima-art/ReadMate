from pathlib import Path
from pypdf import PdfReader

from simple_book_processor import detect_chapters_hybrid

pdf_path = Path("uploads/alicesadventurescarroll.pdf")

if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found: {pdf_path}")

reader = PdfReader(str(pdf_path))

pages = []

for page_number, page in enumerate(reader.pages, start=1):
    pages.append({
        "page_number": page_number,
        "content": page.extract_text() or ""
    })

print(f"PDF pages extracted: {len(pages)}")

chapters = detect_chapters_hybrid(pages)

print(f"\nChapters detected: {len(chapters)}")

for chapter in chapters:
    print(
        f"Chapter {chapter['chapter_number']} | "
        f"Page {chapter['start_page']} | "
        f"{chapter['title']}"
    )