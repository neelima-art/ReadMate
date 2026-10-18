import os

from pypdf import PdfReader
from ebooklib import epub
from bs4 import BeautifulSoup


def extract_pdf_text(file_path):
    """
    Extract text from a PDF.
    """

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n\n".join(pages)


def extract_epub_text(file_path):
    """
    Extract readable text from an EPUB.
    """

    book = epub.read_epub(file_path)

    chapters = []

    for item in book.get_items():

        if item.get_type() == 9:  # XHTML document

            soup = BeautifulSoup(
                item.get_content(),
                "html.parser"
            )

            text = soup.get_text(
                separator="\n",
                strip=True
            )

            if text:
                chapters.append(text)

    return "\n\n".join(chapters)


def extract_book_text(file_path):
    """
    Automatically choose the correct
    extractor based on file extension.
    """

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".epub":
        return extract_epub_text(file_path)

    else:
        raise ValueError(
            "Unsupported book format. "
            "Only PDF and EPUB are supported."
        )

def extract_chapters(text):

    import re

    pattern = r"(?im)^\s*Chapter\s+(\d+)\s+Summary\s*:?\s*([A-Z0-9-]+)?"

    matches = list(re.finditer(pattern, text))

    chapters = []

    for index, match in enumerate(matches):

        chapter_number = int(match.group(1))

        chapter_title = match.group(2) or ""

        start = match.end()

        # Next chapter starts here
        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        content = text[start:end].strip()

        chapters.append({
            "chapter_number": chapter_number,
            "title": chapter_title,
            "content": content
        })

    return chapters

def extract_pdf_pages(file_path):

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "content": text
        })

    return pages

def split_into_paragraphs(text):

    paragraphs = []

    blocks = text.split("\n\n")

    search_position = 0

    for block in blocks:

        content = block.strip()

        if not content:
            continue

        start = text.find(
            content,
            search_position
        )

        if start == -1:
            continue

        end = start + len(content)

        paragraphs.append({
            "content": content,
            "start_offset": start,
            "end_offset": end
        })

        search_position = end

    return paragraphs




if __name__ == "__main__":

    upload_folder = "uploads"

    files = [
        file
        for file in os.listdir(upload_folder)
        if file.lower().endswith((".pdf", ".epub"))
    ]

    if not files:
        print("No PDF or EPUB files found.")
        exit()

    print("Books found:\n")

    for index, file in enumerate(files, start=1):
        print(f"{index}. {file}")

    selected = int(
        input("\nEnter book number to process: ")
    )

    file_path = os.path.join(
        upload_folder,
        files[selected - 1]
    )

    print("\nProcessing:", files[selected - 1])

    text = extract_book_text(file_path)

    print("\nTotal characters:", len(text))

    # --------------------------------------------
    # EXTRACT CHAPTERS
    # --------------------------------------------

    chapters = extract_chapters(text)

    print(
        "\nChapters extracted:",
        len(chapters)
    )

    # --------------------------------------------
    # SHOW FIRST 5 CHAPTERS
    # --------------------------------------------

    for chapter in chapters[:5]:

        print("\n")
        print("=" * 70)

        print(
            f"CHAPTER {chapter['chapter_number']}"
        )

        print(
            f"TITLE: {chapter['title']}"
        )

        print("=" * 70)

        print(
            chapter["content"][:1000]
        )

        print("\n[END PREVIEW]")
