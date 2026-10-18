import re

from pypdf import PdfReader

from database import SessionLocal
from models import Book, BookPage, Chapter


def extract_pages(file_path):

    reader = PdfReader(file_path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "content": text.strip()
        })

    return pages


def find_chapters(pages):
    """Find standard chapter headings without using the AI."""
    pattern = re.compile(
        r"^\s*CHAPTER\s+([IVXLCDM]+|\d+)\b(?:\s*[:.\-–]\s*(.*))?\s*$",
        re.IGNORECASE,
    )
    candidates = []
    for page in pages:
        lines = page["content"].splitlines()
        for index, line in enumerate(lines):
            match = pattern.fullmatch(line.strip())
            if not match:
                continue
            token = match.group(1)
            number = int(token) if token.isdigit() else roman_to_int(token)
            if number < 1:
                continue
            title = (match.group(2) or "").strip()
            if not title:
                # Look ahead for the chapter title, skipping blank lines.
                for following in lines[index + 1:index + 6]:
                    following = following.strip()
            
                    if not following:
                        continue
            
                    # Don't accidentally use another chapter heading.
                    if pattern.fullmatch(following):
                        break
            
                    # Avoid treating a long paragraph as the title.
                    if len(following) <= 100 and len(following.split()) <= 15:
                        title = following
                    break
            candidates.append({
                "chapter_number": number,
                "title": title,
                "start_page": page["page_number"],
            })
    return select_chapter_sequence(candidates)


def select_chapter_sequence(candidates):
    """Prefer the longest ordered chapter run, ignoring TOC duplicates."""
    if not candidates:
        return []
    candidates = sorted(candidates, key=lambda c: (c["start_page"], c["chapter_number"]))
    # A chapter can begin on the same page as the previous chapter ends;
    # the chapter table is page-granular, so retain only one start per page.
    best = []
    for start in range(len(candidates)):
        run = [candidates[start]]
        for candidate in candidates[start + 1:]:
            if (candidate["chapter_number"] == run[-1]["chapter_number"] + 1
                    and candidate["start_page"] > run[-1]["start_page"]):
                run.append(candidate)
        if not best or len(run) > len(best) or (
            len(run) == len(best) and run[0]["start_page"] > best[0]["start_page"]
        ):
            best = run
    return best


def backend_detection_is_reliable(chapters, pages):
    """Conservative heuristic; not proof of complete chapter coverage."""
    if len(chapters) < 2:
        return False
    if chapters[0]["chapter_number"] != 1:
        return False
    if any(chapters[i]["chapter_number"] != i + 1 for i in range(len(chapters))):
        return False
    starts = [c["start_page"] for c in chapters]
    if starts != sorted(set(starts)):
        return False
    # A large unexplained gap may mean title-only chapters were missed.
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    if gaps and max(gaps) > max(40, 3 * sorted(gaps)[len(gaps) // 2]):
        return False
    return True


def detect_chapters_hybrid(pages):
    """Fast backend detection first; AI only when the result is uncertain."""
    regex_chapters = find_chapters(pages)
    if backend_detection_is_reliable(regex_chapters, pages):
        print("Backend chapter detection accepted:", len(regex_chapters))
        return regex_chapters

    print("Backend chapter detection uncertain; trying AI fallback")
    all_lines, line_pages = [], []
    for page in pages:
        for line in page["content"].splitlines():
            all_lines.append(line)
            line_pages.append(page["page_number"])

    try:
        from ai_chapter_detector import detect_chapters
        detected = detect_chapters(all_lines)
        ai_candidates = []
        seen_pages = set()
        for item in detected:
            index = item.get("line_number")
            if not isinstance(index, int) or not (0 <= index < len(all_lines)):
                continue
            heading = all_lines[index].strip()
            page_number = line_pages[index]
            if not heading or len(heading) > 160 or page_number in seen_pages:
                continue
            ai_candidates.append({
                "chapter_number": len(ai_candidates) + 1,
                "title": str(item.get("title") or heading).strip()[:200],
                "start_page": page_number,
            })
            seen_pages.add(page_number)

        ai_candidates.sort(key=lambda c: c["start_page"])
        for number, chapter in enumerate(ai_candidates, start=1):
            chapter["chapter_number"] = number
        if len(ai_candidates) >= 2:
            print("AI fallback detected chapters:", len(ai_candidates))
            return ai_candidates
    except Exception as exc:
        print("AI chapter detection unavailable:", exc)

    # Avoid saving incomplete, low-confidence chapter lists.
    print("No reliable chapter sequence detected")
    return []


def roman_to_int(roman):

    values = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000
    }

    total = 0
    previous = 0

    for char in reversed(
        roman.upper()
    ):

        value = values[char]

        if value < previous:

            total -= value

        else:

            total += value

        previous = value

    return total

def assign_end_pages(
    chapters,
    total_pages
):

    for index, chapter in enumerate(
        chapters
    ):

        if index + 1 < len(chapters):

            next_chapter = chapters[
                index + 1
            ]

            chapter["end_page"] = (
                next_chapter["start_page"] - 1
            )

        else:

            chapter["end_page"] = total_pages

    return chapters

def get_chapter_content(
    pages,
    start_page,
    end_page
):

    content = []

    for page in pages:

        page_number = page["page_number"]

        if (
            start_page
            <= page_number
            <= end_page
        ):

            if page["content"]:

                content.append(
                    page["content"]
                )

    return "\n\n".join(content)

def process_book(book_id, file_path):

    # -----------------------------
    # 1. Extract book metadata
    # -----------------------------

    metadata = extract_book_metadata(file_path)

    title = metadata["title"]
    author = metadata["author"]


    # -----------------------------
    # 2. Extract PDF pages
    # -----------------------------

    pages = extract_pages(file_path)

    print("Title:", title)
    print("Author:", author)
    print("Total pages:", len(pages))


    # -----------------------------
    # 3. Open database
    # -----------------------------

    db = SessionLocal()

    try:

        # Detect and validate before touching existing database records.
        chapters = detect_chapters_hybrid(pages)
        if not chapters:
            raise ValueError(
                "No reliable chapters detected. Existing book data was not changed."
            )
        chapters = assign_end_pages(chapters, len(pages))

        # Replace data in one transaction only after successful detection.
        db.query(BookPage).filter(
            BookPage.book_id == book_id
        ).delete()

        db.query(Chapter).filter(
            Chapter.book_id == book_id
        ).delete()


        # -----------------------------
        # 4. Save every PDF page
        # -----------------------------

        for page in pages:

            db.add(
                BookPage(
                    book_id=book_id,
                    page_number=page["page_number"],
                    content=page["content"]
                )
            )


        # -----------------------------
        # 5. Detect chapters
        # -----------------------------


        print(
            "Chapters found:",
            len(chapters)
        )


        # -----------------------------
        # 6. Save chapters
        # -----------------------------

        for chapter in chapters:

            content = get_chapter_content(
                pages,
                chapter["start_page"],
                chapter["end_page"]
            )

            db.add(
                Chapter(
                    book_id=book_id,
                    chapter_number=chapter["chapter_number"],
                    title=chapter["title"],
                    start_page=chapter["start_page"],
                    end_page=chapter["end_page"],
                    content=content
                )
            )


        # -----------------------------
        # 7. Update book metadata
        # -----------------------------

        book = (
            db.query(Book)
            .filter(Book.book_id == book_id)
            .first()
        )

        if book:

            if title:
                book.title = title

            if author:
                book.author = author

            book.file_path = file_path


        db.commit()


        print("Book processing completed.")


        return {
            "title": title,
            "author": author,
            "total_pages": len(pages),
            "chapters": chapters
        }


    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def extract_book_metadata(file_path):

    reader = PdfReader(file_path)

    title = None
    author = None

    # 1. Try PDF metadata first
    metadata = reader.metadata

    if metadata:
        if metadata.title:
            title = metadata.title.strip()

        if metadata.author:
            author = metadata.author.strip()

    # 2. If metadata is missing, search first few pages
    if not title or not author:

        first_pages = []

        for page in reader.pages[:10]:

            text = page.extract_text() or ""

            first_pages.append(text)

        text = "\n".join(first_pages)

        # Look for:
        # Title: The Lost World
        title_match = re.search(
            r"(?im)^Title:\s*(.+)$",
            text
        )

        if title_match and not title:
            title = title_match.group(1).strip()

        # Look for:
        # Author: Arthur Conan Doyle
        author_match = re.search(
            r"(?im)^Author(?:\(s\))?:\s*(.+)$",
            text
        )

        if author_match and not author:
            author = author_match.group(1).strip()

    return {
        "title": title,
        "author": author
    }

