from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from simple_book_processor import process_book
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import sys

PREDICTIVE_AI_DIR = Path(__file__).resolve().parents[2] / "predictive_ai"

if str(PREDICTIVE_AI_DIR) not in sys.path:
    sys.path.insert(0, str(PREDICTIVE_AI_DIR))

from predict import predict_difficulty


import os
import shutil
import time
import json
import uuid
from pydantic import BaseModel, Field

from database import Base, engine, SessionLocal
from models import (
    Book,
    ReadingProgress,
    Character,
    CharacterRelationship,
    Chapter,
    BookPage,
    ChatSession,
    ChatMessage,
    PageAnalysis
)

class AnalyzePageRequest(BaseModel):
    page_number: int = Field(ge=1)

Base.metadata.create_all(bind=engine)

load_dotenv()

app = FastAPI(title="ReadMate API")

# Serve uploaded book covers and files
BACKEND_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = BACKEND_DIR / "uploads"

app.mount(
    "/uploads",
    StaticFiles(directory=str(UPLOADS_DIR)),
    name="uploads"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5177",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5177",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_ai_json_response(response):
    """
    Parse an AI JSON response.
    Raise ValueError if the response is empty or invalid.
    """
    text = (response.output_text or "").strip()

    if not text:
        raise ValueError("AI returned an empty response")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"AI returned invalid JSON: {exc}"
        ) from exc


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()



def get_reader_chapter(db: Session, book_id: str) -> int:
    """Return the reading boundary stored by the backend."""
    progress = (
        db.query(ReadingProgress)
        .filter(ReadingProgress.book_id == book_id)
        .first()
    )

    if not progress:
        return 1

    return max(1, progress.current_chapter or 1)

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "ReadMate backend is running"
    }


# Get all books
@app.get("/api/books")
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()

    return books


# Add a book
@app.post("/api/books")
def create_book(
    book_id: str,
    title: str,
    author: str,
    db: Session = Depends(get_db)
):
    new_book = Book(
        book_id=book_id,
        title=title,
        author=author
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book

@app.get("/api/books/{book_id}")
def get_book(book_id: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()

    if not book:
        return {"error": "Book not found"}

    return book

@app.get("/api/books/{book_id}/progress")
def get_progress(
    book_id: str,
    db: Session = Depends(get_db)
):
    progress = (
        db.query(ReadingProgress)
        .filter(ReadingProgress.book_id == book_id)
        .first()
    )

    if not progress:
        return {
            "book_id": book_id,
            "current_chapter": 1,
            "current_position": 0,
            "progress": 0,
            "last_read": None
        }

    return progress


@app.post("/api/books/{book_id}/progress")
def save_progress(
    book_id: str,
    current_chapter: int,
    current_position: int,
    progress_value: float = 0,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    if current_position < 0:
        raise HTTPException(status_code=400, detail="Reading position cannot be negative.")

    saved = db.query(ReadingProgress).filter(
        ReadingProgress.book_id == book_id
    ).first()
    if saved is None:
        saved = ReadingProgress(
            book_id=book_id,
            current_chapter=1,
            current_position=0,
            progress=0
        )
        db.add(saved)

    # Monotonic progress: revisiting an earlier page must not lower progress.
    furthest = max(saved.current_position or 0, current_position)
    saved.current_position = furthest

    chapters = db.query(Chapter).filter(
        Chapter.book_id == book_id
    ).order_by(Chapter.chapter_number).all()
    reached_chapters = [
        c.chapter_number for c in chapters
        if c.start_page is not None and c.start_page <= furthest
    ]
    if reached_chapters:
        saved.current_chapter = max(
            saved.current_chapter or 1, max(reached_chapters)
        )
    else:
        saved.current_chapter = max(saved.current_chapter or 1, 1)

    total_pages = db.query(BookPage).filter(
        BookPage.book_id == book_id
    ).count()
    if total_pages > 0:
        percent = round(min(100, furthest / total_pages * 100))
    else:
        # Fallback for books without stored page rows.
        percent = round(max(0, min(100, progress_value)))
    saved.progress = max(saved.progress or 0, percent)
    db.commit()
    db.refresh(saved)
    return {
        "book_id": book_id,
        "current_chapter": saved.current_chapter,
        "current_position": saved.current_position,
        "progress": saved.progress,
        "last_read": saved.last_read,
    }


@app.get("/api/books/{book_id}/characters")
def get_characters(
    book_id: str,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.book_id == book_id
    ).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    current_chapter = get_reader_chapter(db, book_id)

    characters = (
        db.query(Character)
        .filter(
            Character.book_id == book_id,
            Character.revealed_in_chapter <= current_chapter
        )
        .all()
    )

    return characters



@app.get("/api/books/{book_id}/relationships")
def get_relationships(
    book_id: str,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.book_id == book_id
    ).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    current_chapter = get_reader_chapter(db, book_id)

    relationships = (
        db.query(CharacterRelationship)
        .filter(
            CharacterRelationship.book_id == book_id,
            CharacterRelationship.revealed_in_chapter <= current_chapter
        )
        .all()
    )

    return relationships


@app.post("/api/books/{book_id}/relationships")
def create_relationship(
    book_id: str,
    character_id: str,
    related_character_id: str,
    relationship_type: str,
    description: str = "",
    revealed_in_chapter: int = 1,
    db: Session = Depends(get_db)
):
    new_relationship = CharacterRelationship(
        book_id=book_id,
        character_id=character_id,
        related_character_id=related_character_id,
        relationship_type=relationship_type,
        description=description,
        revealed_in_chapter=revealed_in_chapter
    )

    db.add(new_relationship)
    db.commit()
    db.refresh(new_relationship)

    return new_relationship


def normalize_character_name(name: str) -> str:
    return " ".join(name.strip().casefold().split())


def parse_aliases(aliases):
    if not aliases:
        return []

    try:
        result = json.loads(aliases)
        if isinstance(result, list):
            return [
                str(alias).strip()
                for alias in result
                if str(alias).strip()
            ]
    except (json.JSONDecodeError, TypeError):
        pass

    return [
        alias.strip()
        for alias in aliases.split(",")
        if alias.strip()
    ]


@app.post("/api/books/{book_id}/analyze-page")
def analyze_book_page(
    book_id: str,
    request: AnalyzePageRequest,
    db: Session = Depends(get_db),
):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_actual_api_key_here":
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is not configured.",
        )

    book = db.query(Book).filter(
        Book.book_id == book_id
    ).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")

    page = db.query(BookPage).filter(
        BookPage.book_id == book_id,
        BookPage.page_number == request.page_number,
    ).first()

    if not page:
        raise HTTPException(
            status_code=404,
            detail="Page text not found. Check that the book was processed.",
        )

    analysis = db.query(PageAnalysis).filter(
        PageAnalysis.book_id == book_id,
        PageAnalysis.page_number == request.page_number,
    ).first()

    if analysis and analysis.status == "completed":
        return {
            "message": "Page already analyzed.",
            "already_processed": True,
            "page_number": request.page_number,
        }

    if analysis and analysis.status == "processing":
        raise HTTPException(
            status_code=409,
            detail="This page is already being analyzed.",
        )

    if not analysis:
        analysis = PageAnalysis(
            book_id=book_id,
            page_number=request.page_number,
            status="processing",
        )
        db.add(analysis)
    else:
        analysis.status = "processing"
        analysis.error_message = None

    db.commit()

    try:
        page_text = (page.content or "").strip()

        if not page_text:
            analysis.status = "completed"
            db.commit()

            return {
                "message": "Page has no extractable text.",
                "page_number": request.page_number,
                "characters_saved": 0,
                "relationships_saved": 0,
            }

        chapter = db.query(Chapter).filter(
            Chapter.book_id == book_id,
            Chapter.start_page <= request.page_number,
            Chapter.end_page >= request.page_number,
        ).first()

        chapter_number = chapter.chapter_number if chapter else 1

        existing_characters = db.query(Character).filter(
            Character.book_id == book_id
        ).all()

        known_characters = [
            {
                "name": character.name,
                "aliases": parse_aliases(character.aliases),
                "role": character.role or "",
            }
            for character in existing_characters
        ]

        client = OpenAI(api_key=api_key, default_headers={"Accept-Encoding": "identity"})

        # Structured output prevents malformed JSON; retry empty/incomplete replies.
        analysis_instructions = """
You are ReadMate, a careful book-character analyst.

Analyze ONLY the supplied page text. Do not use outside knowledge
or reveal information from later pages.

Return valid JSON with exactly these keys:
{
  "characters": [
    {
      "name": "canonical character name",
      "aliases": [],
      "role": "",
      "description": "",
      "status": "",
      "relationship_to_main": ""
    }
  ],
  "relationships": [
    {
      "character_name": "",
      "related_character_name": "",
      "relationship_type": "",
      "description": ""
    }
  ]
}

Rules:
- Identify only characters supported by the page.
- Reuse existing character names and aliases when appropriate.
- Do not create duplicate identities for the same character.
- Include only relationships supported by the supplied text.
- Relationships may connect any two characters.
- Do not assume a book has only one main character.
- Use empty strings or empty lists for unknown information.
- Do not invent facts or reveal future events.
- Return JSON only, without Markdown fences.
"""
        analysis_input = json.dumps({
            "book_title": book.title,
            "page_number": request.page_number,
            "chapter_number": chapter_number,
            "known_characters": known_characters,
            "page_text": page_text[:12000],
        })

        string_field = {"type": "string"}
        character_fields = [
            "name", "aliases", "role", "description", "status",
            "relationship_to_main",
        ]
        relationship_fields = [
            "character_name", "related_character_name",
            "relationship_type", "description",
        ]
        character_properties = {
            key: ({"type": "array", "items": string_field}
                  if key == "aliases" else string_field)
            for key in character_fields
        }
        relationship_properties = {
            key: string_field for key in relationship_fields
        }
        output_schema = {
            "type": "object",
            "properties": {
                "characters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": character_properties,
                        "required": character_fields,
                        "additionalProperties": False,
                    },
                },
                "relationships": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": relationship_properties,
                        "required": relationship_fields,
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["characters", "relationships"],
            "additionalProperties": False,
        }

        result = None
        last_parse_error = None
        for attempt in range(2):
            response = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
                instructions=analysis_instructions,
                input=analysis_input,
                max_output_tokens=5000,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "readmate_page_characters",
                        "schema": output_schema,
                        "strict": True,
                    }
                },
            )
            try:
                if response.status == "incomplete":
                    details = getattr(response, "incomplete_details", None)
                    reason = getattr(details, "reason", "unknown")
                    raise ValueError(f"AI response incomplete: {reason}")

                candidate = parse_ai_json_response(response)
                if not isinstance(candidate, dict):
                    raise ValueError("AI response must be a JSON object.")
                if not isinstance(candidate.get("characters"), list):
                    raise ValueError("Characters must be a list.")
                if not isinstance(candidate.get("relationships"), list):
                    raise ValueError("Relationships must be a list.")
                result = candidate
                break
            except (ValueError, TypeError, AttributeError) as exc:
                last_parse_error = exc
                print(
                    f"[ReadMate AI RETRY] book={book_id}, "
                    f"page={request.page_number}, attempt={attempt + 1}, "
                    f"reason={exc}",
                    flush=True,
                )

        if result is None:
            raise ValueError(
                f"AI response failed after 2 attempts: {last_parse_error}"
            )

        detected_characters = result["characters"]
        detected_relationships = result["relationships"]

        # Match characters by canonical name and aliases.
        name_index = {}

        for character in existing_characters:
            candidates = [
                character.name,
                *parse_aliases(character.aliases),
            ]

            for candidate in candidates:
                normalized = normalize_character_name(candidate)
                if normalized:
                    name_index[normalized] = character

        characters_saved = 0
        relationships_saved = 0

        # Create new characters or enrich existing records.
        for item in detected_characters:
            if not isinstance(item, dict):
                continue

            name = item.get("name")

            if not isinstance(name, str) or not name.strip():
                continue

            name = name.strip()
            aliases = item.get("aliases", [])

            if not isinstance(aliases, list):
                aliases = []

            aliases = [
                alias.strip()
                for alias in aliases
                if isinstance(alias, str) and alias.strip()
            ]

            character = None

            for candidate in [name, *aliases]:
                character = name_index.get(
                    normalize_character_name(candidate)
                )
                if character:
                    break

            if character is None:
                character = Character(
                    character_id=str(uuid.uuid4()),
                    book_id=book_id,
                    name=name,
                    aliases=json.dumps(aliases),
                    role=item.get("role", "").strip(),
                    description=item.get("description", "").strip(),
                    status=item.get("status", "").strip(),
                    first_appearance=request.page_number,
                    revealed_in_chapter=chapter_number,
                    relationship_to_main=(
                        item.get("relationship_to_main", "").strip()
                    ),
                )

                db.add(character)
                db.flush()
                characters_saved += 1

            else:
                # Never replace established information with empty values.
                for field in (
                    "role",
                    "description",
                    "status",
                    "relationship_to_main",
                ):
                    value = item.get(field)

                    if (
                        isinstance(value, str)
                        and value.strip()
                        and not getattr(character, field)
                    ):
                        setattr(character, field, value.strip())

                old_aliases = parse_aliases(character.aliases)

                for alias in aliases:
                    existing_names = {
                        normalize_character_name(value)
                        for value in old_aliases
                    }

                    if (
                        normalize_character_name(alias) not in existing_names
                        and normalize_character_name(alias)
                        != normalize_character_name(character.name)
                    ):
                        old_aliases.append(alias)

                character.aliases = json.dumps(old_aliases)

            # Make this character available for relationship matching.
            for candidate in [
                character.name,
                *parse_aliases(character.aliases),
                name,
                *aliases,
            ]:
                normalized = normalize_character_name(candidate)

                if normalized:
                    name_index[normalized] = character

        # Save relationships between any two identified characters.
        for item in detected_relationships:
            if not isinstance(item, dict):
                continue

            first_name = item.get("character_name")
            second_name = item.get("related_character_name")
            relation_type = item.get("relationship_type")

            if not all(
                isinstance(value, str) and value.strip()
                for value in (first_name, second_name, relation_type)
            ):
                continue

            first = name_index.get(
                normalize_character_name(first_name)
            )
            second = name_index.get(
                normalize_character_name(second_name)
            )

            if (
                not first
                or not second
                or first.character_id == second.character_id
            ):
                continue

            relation_type = relation_type.strip()

            # Check both directions to reduce duplicate relationships.
            existing_relation = db.query(
                CharacterRelationship
            ).filter(
                CharacterRelationship.book_id == book_id,
                CharacterRelationship.relationship_type.ilike(
                    relation_type
                ),
                (
                    (
                        CharacterRelationship.character_id
                        == first.character_id
                    )
                    & (
                        CharacterRelationship.related_character_id
                        == second.character_id
                    )
                )
                |
                (
                    (
                        CharacterRelationship.character_id
                        == second.character_id
                    )
                    & (
                        CharacterRelationship.related_character_id
                        == first.character_id
                    )
                ),
            ).first()

            description = item.get("description", "")

            if existing_relation:
                if (
                    isinstance(description, str)
                    and description.strip()
                    and not existing_relation.description
                ):
                    existing_relation.description = description.strip()

                continue

            db.add(
                CharacterRelationship(
                    book_id=book_id,
                    character_id=first.character_id,
                    related_character_id=second.character_id,
                    relationship_type=relation_type,
                    description=(
                        description.strip()
                        if isinstance(description, str)
                        else ""
                    ),
                    revealed_in_chapter=chapter_number,
                )
            )

            relationships_saved += 1

        analysis.status = "completed"
        analysis.error_message = None
        db.commit()

        return {
            "message": "Page analyzed successfully.",
            "already_processed": False,
            "page_number": request.page_number,
            "chapter_number": chapter_number,
            "characters_saved": characters_saved,
            "relationships_saved": relationships_saved,
        }

    except OpenAIError as exc:
        db.rollback()

        failed = db.query(PageAnalysis).filter(
            PageAnalysis.book_id == book_id,
            PageAnalysis.page_number == request.page_number,
        ).first()

        if failed:
            failed.status = "failed"
            failed.error_message = "OpenAI request failed."
            db.commit()

        raise HTTPException(
            status_code=502,
            detail=(
                "AI analysis failed. Check your API key, "
                "model access, and API billing."
            ),
        ) from exc

    except (ValueError, TypeError, AttributeError) as exc:
        db.rollback()
        
        print(
            f"[ReadMate PARSING ERROR] "
            f"book={book_id}, page={request.page_number}, "
            f"type={type(exc).__name__}, error={exc}",
            flush=True
        )

        failed = db.query(PageAnalysis).filter(
            PageAnalysis.book_id == book_id,
            PageAnalysis.page_number == request.page_number,
        ).first()

        if failed:
            failed.status = "failed"
            failed.error_message = "Invalid or unexpected AI response."
            db.commit()

        raise HTTPException(
            status_code=502,
            detail="The AI returned data that could not be processed.",
        ) from exc


@app.post("/api/books/upload")
async def upload_book(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.lower().endswith(
        (".pdf", ".epub")
    ):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and EPUB files are supported."
        )


    # -----------------------------
    # Save original file
    # -----------------------------

    # Save uploads relative to this backend
    backend_dir = Path(__file__).resolve().parent
    upload_folder = backend_dir / "uploads"
    upload_folder.mkdir(parents=True, exist_ok=True)

    # Prevent filenames from containing directory paths
    safe_filename = Path(
        file.filename.replace("\\", "/")
    ).name

    # Absolute path used for saving and processing
    saved_file_path = upload_folder / safe_filename

    # Portable relative path stored in SQLite
    file_path = (Path("uploads") / safe_filename).as_posix()

    with open(
        saved_file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # -----------------------------
    # Create book ID
    # -----------------------------

    book_id = os.path.splitext(
        file.filename
    )[0]

    book_id = (
        book_id
        .lower()
        .replace(" ", "-")
    )


    # -----------------------------
    # Check existing book
    # -----------------------------

    existing_book = (
        db.query(Book)
        .filter(
            Book.book_id == book_id
        )
        .first()
    )


    if existing_book:

        print("Book already exists. Reprocessing...")

        existing_book.file_path = file_path
        db.commit()
        result = process_book(
            existing_book.book_id,
            str(saved_file_path)
        )
    
        return {
            "message": "Book reprocessed successfully",
    
            "book": {
                "book_id": existing_book.book_id,
                "title": result["title"],
                "author": result["author"],
                "total_pages": result["total_pages"]
            },
    
            "chapters": result["chapters"]
        }


    # -----------------------------
    # Create initial book
    # -----------------------------

    new_book = Book(
        book_id=book_id,
        title="Processing...",
        author="",
        file_path=file_path
    )

    db.add(new_book)

    db.commit()

    db.refresh(new_book)


    # -----------------------------
    # Process the book
    # -----------------------------

    result = process_book(
        book_id,
        str(saved_file_path)
    )


    # -----------------------------
    # Return result
    # -----------------------------

    return {
        "message": "Book uploaded and processed successfully",

        "book": {
            "book_id": book_id,
            "title": result["title"],
            "author": result["author"],
            "total_pages": result["total_pages"]
        },

        "chapters": result["chapters"]
    }
@app.get("/api/books/{book_id}/file")
def get_book_file(
    book_id: str,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.book_id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    if not book.file_path:
        raise HTTPException(
            status_code=404,
            detail="Book file path missing"
        )

    backend_dir = Path(__file__).resolve().parent
    uploads_dir = (backend_dir / "uploads").resolve()

    stored = book.file_path.replace("\\", "/")
    normalized = Path(stored)

    candidates = [
        backend_dir / normalized,
        uploads_dir / normalized.name,
    ]

    for candidate in candidates:
        resolved = candidate.resolve()

        if (
            resolved.is_relative_to(uploads_dir)
            and resolved.is_file()
        ):
            return FileResponse(
                str(resolved),
                media_type="application/pdf"
            )

    raise HTTPException(
        status_code=404,
        detail="PDF file does not exist"
    )

# Get chapters for a book
@app.get("/api/books/{book_id}/chapters")
def get_chapters(
    book_id: str,
    db: Session = Depends(get_db)
):
    chapters = (
        db.query(Chapter)
        .filter(Chapter.book_id == book_id)
        .order_by(Chapter.chapter_number)
        .all()
    )

    return chapters


# =========================
# CHAT REQUEST SCHEMA
# =========================


class ChatMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=8000)



# =========================
# CREATE A NEW CHAT
# =========================

@app.post("/api/books/{book_id}/chats")
def create_chat(
    book_id: str,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.book_id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    chat = ChatSession(
        book_id=book_id,
        title="New chat"
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return {
        "id": chat.id,
        "book_id": chat.book_id,
        "title": chat.title,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at
    }


# =========================
# LIST CHATS FOR A BOOK
# =========================

@app.get("/api/books/{book_id}/chats")
def get_book_chats(
    book_id: str,
    db: Session = Depends(get_db)
):
    chats = (
        db.query(ChatSession)
        .filter(ChatSession.book_id == book_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )

    return [
        {
            "id": chat.id,
            "book_id": chat.book_id,
            "title": chat.title,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        }
        for chat in chats
    ]


# =========================
# LOAD CHAT MESSAGES
# =========================

@app.get("/api/chats/{chat_id}/messages")
def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db)
):
    chat = db.query(ChatSession).filter(
        ChatSession.id == chat_id
    ).first()

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.created_at, ChatMessage.id)
        .all()
    )

    return [
        {
            "id": message.id,
            "chat_id": message.chat_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at
        }
        for message in messages
    ]


# =========================
# SEND A MESSAGE TO THE AI
# =========================

@app.post("/api/chats/{chat_id}/messages")
def send_chat_message(
    chat_id: int,
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key == "your_actual_api_key_here":
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is not configured in backend/.env"
        )

    chat = db.query(ChatSession).filter(
        ChatSession.id == chat_id
    ).first()

    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat not found"
        )

    book = db.query(Book).filter(
        Book.book_id == chat.book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    # Save the user's message first.
    user_message = ChatMessage(
        chat_id=chat.id,
        role="user",
        content=request.content.strip()
    )

    db.add(user_message)

    if chat.title == "New chat":
        chat.title = request.content.strip()[:60]

    chat.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(user_message)

    # Get only chapters the reader has reached.
    
    # Get the reading boundary from server-side progress.
    current_chapter = get_reader_chapter(db, chat.book_id)

    # Load only chapters the reader has reached.
    chapters = (
        db.query(Chapter)
        .filter(
            Chapter.book_id == chat.book_id,
            Chapter.chapter_number <= current_chapter
        )
        .order_by(Chapter.chapter_number)
        .all()
    )

    # Include only the latest three available chapters.
    context_parts = []

    for chapter in chapters[-3:]:
        if chapter.content:
            context_parts.append(
                f"Chapter {chapter.chapter_number}: "
                f"{chapter.title or ''}\n"
                f"{chapter.content[:4000]}"
            )

    book_context = "\n\n".join(context_parts)

    if not book_context:
        book_context = (
            "No chapter text is available in the database yet. "
            "Do not invent quotations or claim that the book confirms "
            "details you cannot verify."
        )


    instructions = f"""
You are ReadMate, the reader's warm, fun, thoughtful, long-term
reading companion.

YOUR PERSONALITY:
- Feel like a close friend reading alongside the user.
- Be natural, warm, playful, emotionally aware, and curious.
- Enjoy discussing stories, characters, theories, and plot twists.
- Match the reader's energy and communication style.
- If the reader jokes, joke back. If they're upset, be gentle.
- If they are excited, share that excitement naturally.
- You can use casual language, humor, and occasional emojis.
- Do not force slang, emojis, or exaggerated excitement.
- Never sound like a textbook, customer support agent, or lecturer.
- Don't call the reader "bro" unless they use that style themselves.
- Don't pretend to be a human or claim to have personally read
  chapters outside the supplied context.

HOW TO CHAT:
- Treat the conversation as an ongoing book-club friendship.
- React to what the reader says before explaining anything.
- Have opinions and interpretations, but label uncertain theories
  as theories rather than established facts.
- Gossip playfully about characters when the reader wants to.
- Ask interesting follow-up questions occasionally, not every time.
- Avoid robotic openings like "Certainly!" or "Great question!"
- Avoid unnecessary lists and formal explanations.
- Keep casual responses around 1-4 sentences unless the reader
  wants a detailed explanation.
- Remember and build on the conversation history provided.
- Never pretend to remember something outside that history.
- If the reader wants to discuss everyday life, respond warmly
  instead of forcing every conversation back to books.
- Support the reader's independence and real-world friendships.

BOOK INFORMATION:
Title: {book.title}
Author: {book.author or "Unknown"}
Reader's current chapter: {current_chapter}

BOOK CONTEXT AVAILABLE TO YOU:
{book_context}

IMPORTANT SPOILER RULES:
- Never reveal events beyond the reader's reading progress.
- Use only supplied book text and conversation for story facts.
- Do not invent character actions, relationships, or quotations.
- Do not hint at future twists or say things like
  "just wait until you find out."
- If information is missing, say so naturally.
- Distinguish between facts, guesses, and reader theories.

EXAMPLE TONE:
Reader: "I think this character is suspicious."
ReadMate: "Ooh, what gave you that feeling? 👀 I'm curious
whether it's something they said or just their whole vibe."

Reader: "That chapter was heartbreaking."
ReadMate: "Yeah, that sounds like it really hit you. 💙
Which moment stayed with you the most?"

Reader: "Explain what happened."
ReadMate: "Okay, here's how I'm understanding it so far..."
Then explain clearly using the available context.

Your goal is to make reading feel like a shared adventure,
with a companion who is fun to talk to and genuinely useful.
"""


    # Load recent conversation history for continuity.
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat.id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .limit(12)
        .all()
    )

    history.reverse()

    conversation_input = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in history
    ]

    try:
        client = OpenAI(api_key=api_key, default_headers={"Accept-Encoding": "identity"})

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            instructions=instructions,
            input=conversation_input,
            max_output_tokens=1500
        )

        answer = response.output_text.strip()

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="The AI returned an empty response. Please try again."
            )

    except OpenAIError:
        raise HTTPException(
            status_code=502,
            detail=(
                "The AI request failed. Your message was saved. "
                "Check your API key, model access, and API billing."
            )
        )

    # Save the AI response.
    assistant_message = ChatMessage(
        chat_id=chat.id,
        role="assistant",
        content=answer
    )

    db.add(assistant_message)
    chat.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(assistant_message)

    return {
        "user_message": {
            "id": user_message.id,
            "role": user_message.role,
            "content": user_message.content,
            "created_at": user_message.created_at
        },
        "assistant_message": {
            "id": assistant_message.id,
            "role": assistant_message.role,
            "content": assistant_message.content,
            "created_at": assistant_message.created_at
        }
    }

# ==========================================
# ABOUT THIS BOOK - DATABASE ONLY
# ==========================================

@app.get("/api/books/{book_id}/about")
def get_book_about(
    book_id: str,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(
        Book.book_id == book_id
    ).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    total_pages = db.query(BookPage).filter(
        BookPage.book_id == book_id
    ).count()

    total_chapters = db.query(Chapter).filter(
        Chapter.book_id == book_id
    ).count()

    publication_date = (
        getattr(book, "publication_date", None)
        or getattr(book, "published_date", None)
    )

    return {
        "book_id": book.book_id,
        "title": book.title,
        "author": book.author or "Unknown",
        "publication_date": (
            str(publication_date)
            if publication_date else None
        ),
        "genre": getattr(book, "genre", None),
        "total_pages": total_pages,
        "total_chapters": total_chapters
    }


# ==========================================
# PREDICTIVE AI - READING DIFFICULTY
# ==========================================

class DifficultyRequest(BaseModel):
    text: str = Field(min_length=1)


@app.post("/api/predict-difficulty")
def predict_reading_difficulty(request: DifficultyRequest):
    try:
        return predict_difficulty(request.text)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
