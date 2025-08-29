# File: backend/model/comment.py

from sqlalchemy import Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
from datetime import datetime

class Comment(Base):
    """Represents a single anonymous comment on a paper."""
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # The paper this comment belongs to. Indexed for fast lookups.
    paper_id: Mapped[int] = mapped_column(ForeignKey("papers.id"), index=True)
    
    # The content of the comment.
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timestamp for chronological sorting.
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())