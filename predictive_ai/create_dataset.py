
import sys
import csv
from pathlib import Path

from pypdf import PdfReader
from features import extract_features

BACKEND = Path.home() / "datathon2026/readmate/app/ai-reading-companion/backend"
UPLOADS = BACKEND / "uploads"

def extract_pdf_pages(path):
    reader = PdfReader(str(path))

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if len(text.split()) >= 50:
            yield page_number, text

def create_dataset():
    rows = []

    for book_path in sorted(UPLOADS.glob("*.pdf")):
        print(f"Processing: {book_path.name}", flush=True)

        try:
            for page_number, text in extract_pdf_pages(book_path):
                features = extract_features(text)

                rows.append({
                    "book": book_path.name,
                    "page": page_number,
                    **features
                })

        except Exception as error:
            print(f"Error processing {book_path.name}: {error}")

    output = Path("reading_features.csv")

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "book",
                "page",
                "avg_sentence_length",
                "avg_word_length",
                "long_word_ratio",
                "unique_word_ratio"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDataset created: {output}")
    print(f"Total pages analyzed: {len(rows)}")

if __name__ == "__main__":
    create_dataset()

