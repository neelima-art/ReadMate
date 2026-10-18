from database import SessionLocal

from models import BookPage


def build_page_line_mapping(pages):

    all_lines = []

    line_to_page = []

    page_line_ranges = []


    for page in pages:

        page_number = page["page_number"]

        content = page["content"] or ""

        page_lines = content.splitlines()


        start_line = len(all_lines)


        for line in page_lines:

            all_lines.append(line)

            line_to_page.append(page_number)


        end_line = len(all_lines) - 1


        page_line_ranges.append({
            "page_number": page_number,
            "start_line": start_line,
            "end_line": end_line
        })


    return (
        all_lines,
        line_to_page,
        page_line_ranges
    )


def get_chapter_for_page(
    page_number,
    page_line_range,
    detected_chapters,
    line_to_page
):

    if not detected_chapters:

        return None


    page_start_line = page_line_range["start_line"]

    page_end_line = page_line_range["end_line"]


    current_chapter = None


    for index, chapter in enumerate(
        detected_chapters
    ):

        chapter_start_line = chapter["line_number"]


        if index + 1 < len(detected_chapters):

            next_chapter_start = (
                detected_chapters[index + 1]["line_number"]
            )

        else:

            next_chapter_start = float("inf")


        # Page belongs to this chapter if
        # its lines overlap the chapter range.

        if (
            page_end_line >= chapter_start_line
            and page_start_line < next_chapter_start
        ):

            current_chapter = (
                chapter["chapter_number"]
            )


    return current_chapter


def save_book_pages(
    book_id,
    pages,
    detected_chapters
):

    (
        all_lines,
        line_to_page,
        page_line_ranges
    ) = build_page_line_mapping(pages)


    db = SessionLocal()


    try:

        # Remove old page data for this book
        db.query(BookPage).filter(
            BookPage.book_id == book_id
        ).delete()


        saved_pages = []


        for page_range in page_line_ranges:

            page_number = (
                page_range["page_number"]
            )


            chapter_number = get_chapter_for_page(

                page_number,

                page_range,

                detected_chapters,

                line_to_page

            )


            page_content = pages[
                page_number - 1
            ]["content"]


            book_page = BookPage(

                book_id=book_id,

                page_number=page_number,

                chapter_number=chapter_number,

                content=page_content.strip()

            )


            db.add(book_page)

            saved_pages.append(
                book_page
            )


        db.commit()


        for page in saved_pages:

            db.refresh(page)


        return saved_pages


    finally:

        db.close()


def process_book_pages(
    book_id,
    pages,
    detected_chapters
):

    saved_pages = save_book_pages(

        book_id,

        pages,

        detected_chapters

    )


    print(
        f"Saved {len(saved_pages)} PDF pages."
    )


    for page in saved_pages[:10]:

        print(
            f"Page {page.page_number}"
            f" → Chapter "
            f"{page.chapter_number}"
        )


    return saved_pages

