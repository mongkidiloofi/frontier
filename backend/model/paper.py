# File: backend/model/paper.py

from sqlalchemy import String, Integer, Text, Float, Date, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base
from datetime import date, datetime

class Paper(Base):
    # ... all other columns are unchanged ...
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
    year_or_date: Mapped[date] = mapped_column(Date) # Stays as Date type
    category: Mapped[str | None] = mapped_column(String(100))
    replies_data: Mapped[list | None] = mapped_column(JSONB)
    keywords: Mapped[list | None] = mapped_column(JSONB)
    user_tags: Mapped[list[str] | None] = mapped_column(JSONB, server_default='[]')
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    upvotes: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    downvotes: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)

    __table_args__ = (
        Index('ix_papers_keywords_gin', keywords, postgresql_using='gin'),
        Index('ix_papers_user_tags_gin', user_tags, postgresql_using='gin'),
        CheckConstraint("jsonb_array_length(user_tags) <= 3", name="user_tags_max_3"),
    )

    # --- THIS IS THE ROBUST SOLUTION ---
    @validates('year_or_date')
    def validate_year_or_date(self, key, value):
        """
        Intercepts assignments to 'year_or_date' and ensures it's a date object.
        This handles both full date strings from arXiv and year-only strings from OpenReview.
        """
        if isinstance(value, date):
            return value # Already a date object, pass through.
            
        if isinstance(value, str):
            # Try to parse as a full date first (e.g., "2024-05-10")
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                # If that fails, try to parse as just a year (e.g., "2024")
                try:
                    year = int(value)
                    # Default to January 1st of that year
                    return date(year, 1, 1)
                except (ValueError, TypeError):
                    # If all parsing fails, return None
                    return None
        
        # If the value is not a string or date, return None
        return None