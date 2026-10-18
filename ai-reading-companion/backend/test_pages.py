from book_processor import (
    extract_pdf_pages,
    split_into_paragraphs
)


PDF_PATH = "uploads/The Lost World - Arthur Conan Doyle.pdf"


pages = extract_pdf_pages(PDF_PATH)


print("Total PDF pages:", len(pages))


for page in pages[:3]:

    print("\n-------------------------")

    print(
        "PAGE:",
        page["page_number"]
    )

    print(
        page["content"][:500]
    )

    paragraphs = split_into_paragraphs(
        page["content"]
    )

    print(
        "Paragraphs:",
        len(paragraphs)
    )

    for index, paragraph in enumerate(
        paragraphs[:3],
        start=1
    ):

        print(
            f"\nParagraph {index}:"
        )

        print(
            paragraph["content"][:200]
        )