"""Offline smoke test: verifies backend-first chapter detection and AI fallback routing.
Run beside simple_book_processor.py; does not open SQLite or call OpenAI.
"""
import sys
import types
from unittest.mock import patch

from simple_book_processor import detect_chapters_hybrid


def make_page(number, heading):
    return {"page_number": number, "content": f"{heading}\nA story begins here.\nMore story text."}


standard_pages = [make_page(3, "CHAPTER 1"), make_page(9, "CHAPTER 2"), make_page(15, "CHAPTER 3")]
title_pages = [make_page(3, "The Boy Who Lived"), make_page(9, "The Vanishing Glass"), make_page(15, "The Letters from No One")]

fake_ai = types.ModuleType("ai_chapter_detector")
calls = []


def fake_detect(lines):
    calls.append(True)
    return [{"line_number": i, "title": heading} for i, heading in enumerate(lines) if heading in {
        "The Boy Who Lived", "The Vanishing Glass", "The Letters from No One"
    }]


fake_ai.detect_chapters = fake_detect
with patch.dict(sys.modules, {"ai_chapter_detector": fake_ai}):
    regular = detect_chapters_hybrid(standard_pages)
    assert len(regular) == 3, regular
    assert not calls, "AI was called unnecessarily for standard chapters"
    print("PASS: Standard headings detected without AI")

    titled = detect_chapters_hybrid(title_pages)
    assert calls, "AI fallback was not called for title-only headings"
    assert [c["start_page"] for c in titled] == [3, 9, 15], titled
    assert [c["title"] for c in titled] == [
        "The Boy Who Lived", "The Vanishing Glass", "The Letters from No One"
    ], titled
    print("PASS: Title-only headings triggered AI fallback")
    print("PASS: AI headings mapped to real PDF pages")

print("ALL TESTS PASSED — no database or OpenAI calls made")
