from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Float
from .database import Base


class ArxivPaper(Base):
    __tablename__ = "arxiv_papers"

    id: Mapped[int] = mapped_column(primary_key=True)
    arxiv_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    authors: Mapped[dict] = mapped_column(JSONB)
    abstract: Mapped[str] = mapped_column(Text)
    pdf_url: Mapped[str] = mapped_column(String(255))
    submitted_date: Mapped[str] = mapped_column(String(20))
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)