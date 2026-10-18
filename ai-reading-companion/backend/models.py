from sqlalchemy import (
    Column,
    Integer,
    String,
    UniqueConstraint,
    ForeignKey,
    DateTime
)
from sqlalchemy.sql import func
from database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(String, unique=True, index=True)

    title = Column(String)

    author = Column(String)

    description = Column(String, nullable=True)

    cover_top = Column(String, nullable=True)

    cover_title = Column(String, nullable=True)

    file_path = Column(String, nullable=True)


class ReadingProgress(Base):
    __tablename__ = "reading_progress"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(String, unique=True, index=True)

    current_chapter = Column(Integer, default=1)

    current_position = Column(Integer, default=0)

    progress = Column(Integer, default=0)

    last_read = Column(String, nullable=True)

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)

    character_id = Column(String, unique=True, index=True)

    book_id = Column(String, index=True)

    name = Column(String)

    aliases = Column(String, nullable=True)

    role = Column(String, nullable=True)

    description = Column(String, nullable=True)

    status = Column(String, nullable=True)

    first_appearance = Column(Integer, nullable=True)

    revealed_in_chapter = Column(Integer, nullable=True)

    relationship_to_main = Column(String, nullable=True)

class CharacterRelationship(Base):
    __tablename__ = "character_relationships"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(String, index=True)

    character_id = Column(String, index=True)

    related_character_id = Column(String, index=True)

    relationship_type = Column(String)

    description = Column(String, nullable=True)

    revealed_in_chapter = Column(Integer, nullable=True)


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(String, index=True)

    chapter_number = Column(Integer)

    title = Column(String, nullable=True)

    start_page = Column(Integer, nullable=True)

    end_page = Column(Integer, nullable=True)

    content = Column(String, nullable=True)

class BookPage(Base):
    __tablename__ = "book_pages"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(String, index=True)

    page_number = Column(Integer)

    content = Column(String)


from datetime import datetime
from sqlalchemy import DateTime, ForeignKey

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(String, index=True, nullable=False)

    title = Column(String, default="New chat")

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)

    chat_id = Column(
        Integer,
        ForeignKey("chat_sessions.id"),
        index=True,
        nullable=False
    )

    role = Column(String, nullable=False)  # "user" or "assistant"

    content = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)




# class PageParagraph(Base):
#     __tablename__ = "page_paragraphs"

#     id = Column(Integer, primary_key=True, index=True)
#     book_page_id = Column(Integer, index=True)
#     paragraph_number = Column(Integer)
#     content = Column(String)
#     start_offset = Column(Integer)
#     end_offset = Column(Integer)


# class PageChapter(Base):
#     __tablename__ = "page_chapters"

#     id = Column(Integer, primary_key=True, index=True)
#     book_page_id = Column(Integer, index=True)
#     chapter_id = Column(Integer, index=True)
#     start_offset = Column(Integer)
#     end_offset = Column(Integer)


from datetime import datetime
from sqlalchemy import DateTime


class PageAnalysis(Base):
    __tablename__ = "page_analyses"

    id = Column(Integer, primary_key=True, index=True)

    book_id = Column(String, nullable=False, index=True)
    page_number = Column(Integer, nullable=False)

    status = Column(String, default="pending", nullable=False)
    error_message = Column(String, nullable=True)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "book_id",
            "page_number",
            name="uq_page_analysis_book_page"
        ),
    )
