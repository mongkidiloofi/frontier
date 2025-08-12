from litestar import Controller, get
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from dataclasses import dataclass, field

from model.paper import Paper # Import the unified Paper model

# --- DTO DEFINITION ---
# This single, unified DTO will represent any paper sent to the frontend.
# It's designed to handle data from both arXiv and OpenReview gracefully.
@dataclass
class PaperDTO:
    # All required arguments first
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
    reputation_score: float # Moved up
    
    # All optional (defaulted) arguments last
    keywords: list[str] = field(default_factory=list)
    category: str | None = None
    replies_data: dict | None = None

    # The from_model method does not need to change
    @classmethod
    def from_model(cls, model: Paper) -> "PaperDTO":
        return cls(
            id=model.id,
            source=model.source,
            source_id=model.source_id,
            title=model.title,
            authors=[author.get('name', 'Unknown Author') for author in (model.authors or [])],
            abstract=model.abstract,
            paper_url=model.paper_url,
            pdf_url=model.pdf_url,
            venue_or_category=model.venue_or_category,
            year_or_date=model.year_or_date,
            reputation_score=model.reputation_score, # Order doesn't matter when calling with keywords
            keywords=model.keywords or [],
            category=model.category,
            replies_data=model.replies_data
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
        # The unified DTO works for arXiv papers too; extra fields will be None or empty.
        return [PaperDTO.from_model(paper) for paper in db_papers]
    
    @get("/openreview")
    async def list_openreview_papers(self, session: AsyncSession) -> List[PaperDTO]:
        """Gets recent OpenReview papers, sorted by year, then ID."""
        query = select(Paper).where(Paper.source == 'openreview').order_by(Paper.year_or_date.desc(), Paper.id.desc()).limit(50)
        result = await session.execute(query)
        db_papers = result.scalars().all()
        return [PaperDTO.from_model(paper) for paper in db_papers]

    # --- (Stretch Goal for later) A combined endpoint ---
    # @get("/all")
    # async def list_all_papers(self, session: AsyncSession) -> List[PaperDTO]:
    #     """Gets all recent papers from all sources, sorted by date/id."""
    #     query = select(Paper).order_by(Paper.id.desc()).limit(100)
    #     result = await session.execute(query)
    #     db_papers = result.scalars().all()
    #     return [PaperDTO.from_model(paper) for paper in db_papers]