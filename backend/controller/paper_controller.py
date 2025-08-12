from litestar import Controller, get
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from dataclasses import dataclass

from model.paper import Paper # Import the unified Paper model

# --- DTO DEFINITION ---
# A single, unified DTO to represent any paper sent to the frontend.
@dataclass
class PaperDTO:
    id: int
    source: str
    source_id: str
    title: str
    authors: list[str]
    abstract: str | None
    paper_url: str
    pdf_url: str | None
    venue_or_category: str
    year_or_date: str
    reputation_score: float

    @classmethod
    def from_model(cls, model: Paper) -> "PaperDTO":
        return cls(
            id=model.id,
            source=model.source,
            source_id=model.source_id,
            title=model.title,
            authors=[author['name'] for author in model.authors],
            abstract=model.abstract,
            paper_url=model.paper_url,
            pdf_url=model.pdf_url,
            venue_or_category=model.venue_or_category,
            year_or_date=model.year_or_date,
            reputation_score=model.reputation_score
        )

# --- CONTROLLER ---
class PaperController(Controller):
    path = "/api/papers"

    @get("/arxiv")
    async def list_arxiv_papers(self, session: AsyncSession) -> List[PaperDTO]:
        """Gets recent arXiv papers, sorted by reputation score."""
        query = select(Paper).where(Paper.source == 'arxiv').order_by(Paper.reputation_score.desc()).limit(50)
        result = await session.execute(query)
        db_papers = result.scalars().all()
        return [PaperDTO.from_model(paper) for paper in db_papers]
    
    @get("/openreview")
    async def list_openreview_papers(self, session: AsyncSession) -> List[PaperDTO]:
        """Gets recent OpenReview papers, sorted by year, then ID."""
        query = select(Paper).where(Paper.source == 'openreview').order_by(Paper.year_or_date.desc(), Paper.id.desc()).limit(50)
        result = await session.execute(query)
        db_papers = result.scalars().all()
        return [PaperDTO.from_model(paper) for paper in db_papers]