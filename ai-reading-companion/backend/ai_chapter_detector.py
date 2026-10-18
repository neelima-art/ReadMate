import os
import json
import re

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.4-mini"
)


CHUNK_SIZE = 1200


def detect_chapters_in_chunk(lines, start_index):

    numbered_lines = []

    for index, line in enumerate(lines):

        cleaned = line.strip()

        if not cleaned:
            continue

        actual_line_number = start_index + index

        numbered_lines.append(
            f"{actual_line_number}: {cleaned}"
        )

    document = "\n".join(numbered_lines)

    prompt = f"""
You are identifying REAL chapter beginnings in a book.

The extracted text comes from a PDF.

A real chapter may be numbered, Roman-numbered, title-only, or part-based.

Examples:
CHAPTER I
Title of chapter

Chapter 2: The Journey

The Boy Who Lived
[followed by the actual chapter text]

ONE
[followed by chapter text]

PART TWO
[followed by a new section of the book]

Do not require the word "chapter" or a chapter number.
Use context and formatting clues to identify actual starts.

Important rules:

1. Find ACTUAL chapter beginnings.

2. A line such as:

CHAPTER XV

followed by a chapter title is a strong indication
of a real chapter.

3. Ignore the table of contents, running headers, and repeated page titles.

For example, this is NOT a real chapter:

Contents
CHAPTER
I. "THERE ARE HEROISMS ALL ROUND US"
II. "TRY YOUR LUCK WITH PROFESSOR CHALLENGER"
III. "HE IS A PERFECTLY IMPOSSIBLE PERSON"

That is only the Contents section.

4. Do NOT treat references to chapters inside normal paragraphs
as chapter beginnings.

5. Do NOT summarize the book.

6. Do NOT modify the original text.

7. Do NOT invent chapter headings.

8. Preserve the original line number exactly.

9. A chapter heading must occur where the chapter content
actually begins.

10. Title-only headings are valid chapter starts. If the text contains:

CHAPTER XV
"Our Eyes have seen Great Wonders"

return the line number of:

CHAPTER XV

not the line containing the title.

Return ONLY valid JSON:

{{
    "chapters": [
        {{
            "line_number": 5762,
            "chapter_number": 15,
            "title": "Our Eyes have seen Great Wonders"
        }}
    ]
}}

TEXT:

{document}
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    result_text = response.output_text.strip()

    if result_text.startswith("```"):

        result_text = re.sub(
            r"^```(?:json)?\s*",
            "",
            result_text
        )

        result_text = re.sub(
            r"\s*```$",
            "",
            result_text
        )

    result = json.loads(result_text)

    return result.get("chapters", [])


def detect_chapters(lines):

    all_chapters = []

    for start in range(
        0,
        len(lines),
        CHUNK_SIZE
    ):

        end = min(
            start + CHUNK_SIZE,
            len(lines)
        )

        chunk = lines[start:end]

        print(
            f"Analyzing lines {start} - {end}..."
        )

        # Include nearby context so a heading on a chunk boundary
        # can be distinguished from ordinary prose.
        context_start = max(0, start - 30)
        context_end = min(len(lines), end + 30)
        chapters = detect_chapters_in_chunk(
            lines[context_start:context_end],
            context_start
        )
        chapters = [
            chapter for chapter in chapters
            if isinstance(chapter.get("line_number"), int)
            and start <= chapter["line_number"] < end
        ]

        all_chapters.extend(chapters)

    all_chapters.sort(
        key=lambda chapter:
        chapter["line_number"]
    )

    unique = []

    seen_lines = set()

    for chapter in all_chapters:

        line_number = chapter["line_number"]

        if line_number in seen_lines:
            continue

        seen_lines.add(line_number)

        unique.append(chapter)

    for index, chapter in enumerate(unique):

        chapter["chapter_number"] = index + 1

    return unique
