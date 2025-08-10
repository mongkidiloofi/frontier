from litestar import Controller, get
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from model.arxiv_paper import ArxivPaper
from dataclasses import dataclass

# --- DTO DEFINITION ---
@dataclass
class PaperDTO:
    id: int
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    pdf_url: str
    submitted_date: str
    reputation_score: float  # <-- ADD THIS LINE

    @classmethod
    def from_model(cls, model: ArxivPaper) -> "PaperDTO":
        return cls(
            id=model.id,
            arxiv_id=model.arxiv_id,
            title=model.title,
            authors=[author['name'] for author in model.authors],
            abstract=model.abstract,
            pdf_url=model.pdf_url,
            submitted_date=model.submitted_date,
            reputation_score=model.reputation_score  # <-- AND ADD THIS LINE
        )

# --- CONTROLLER ---
class PaperController(Controller):
    path = "/api/papers"

    @get("/arxiv")
    async def list_arxiv_papers(self, session: AsyncSession) -> List[PaperDTO]:
        # Sort by the reputation score, descending.
        query = select(ArxivPaper).order_by(ArxivPaper.reputation_score.desc()).limit(50)
        result = await session.execute(query)
        db_papers = result.scalars().all()
        return [PaperDTO.from_model(paper) for paper in db_papers]