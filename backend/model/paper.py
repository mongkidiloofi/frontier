from sqlalchemy import String, Integer, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base

class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50), index=True)
    source_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    title: Mapped[str] = mapped_column(String(500))
    authors: Mapped[dict] = mapped_column(JSONB)
    abstract: Mapped[str | None] = mapped_column(Text)
    
    paper_url: Mapped[str] = mapped_column(String(255))
    pdf_url: Mapped[str | None]
    
    venue_or_category: Mapped[str] = mapped_column(String(200))
    year_or_date: Mapped[str] = mapped_column(String(20))
    
    # This will store the final extracted category, e.g., "Accept (poster)"
    category: Mapped[str | None] = mapped_column(String(100))
    
    # This stores the raw list of all review/comment data
    replies_data: Mapped[list | None] = mapped_column(JSONB)
    
    keywords: Mapped[list | None] = mapped_column(JSONB)
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)