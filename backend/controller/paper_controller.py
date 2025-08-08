from litestar import Controller, get
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from model.arxiv_paper import ArxivPaper
from dataclasses import dataclass # <-- IMPORT dataclass

# --- DTO DEFINITION ---
# 1. Define a simple class that represents the JSON you want to send.
# This is our Data Transfer Object (DTO).
@dataclass
class PaperDTO:
    id: int
    arxiv_id: str
    title: str
    # We'll use a simple list of strings for authors in the DTO
    authors: list[str]
    abstract: str
    pdf_url: str
    submitted_date: str

    # 2. Add a helper method to create a DTO from a SQLAlchemy model instance.
    @classmethod
    def from_model(cls, model: ArxivPaper) -> "PaperDTO":
        return cls(
            id=model.id,
            arxiv_id=model.arxiv_id,
            title=model.title,
            # The authors in the model are a list of dicts, e.g., [{'name': 'A. B.'}]
            # We transform it into a simple list of strings for the DTO.
            authors=[author['name'] for author in model.authors],
            abstract=model.abstract,
            pdf_url=model.pdf_url,
            submitted_date=model.submitted_date
        )

# --- CONTROLLER ---
class PaperController(Controller):
    path = "/api/papers"

    # 3. Update the return type hint of your handler to use the DTO.
    @get("/arxiv")
    async def list_arxiv_papers(self, session: AsyncSession) -> List[PaperDTO]:
        """Gets the most recent arXiv papers from the database."""
        query = select(ArxivPaper).order_by(ArxivPaper.submitted_date.desc()).limit(50)
        result = await session.execute(query)
        
        # Get the SQLAlchemy model instances from the database result
        db_papers = result.scalars().all()
        
        # 4. Convert each SQLAlchemy model instance into a DTO instance.
        #    A list comprehension is a clean way to do this.
        return [PaperDTO.from_model(paper) for paper in db_papers]