from litestar import Controller, get, post, delete, Response, status_codes
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from dataclasses import dataclass, field

from model.paper import Paper
from model.paper_repository import paper_repository
from services.ranking_service import ranking_service, RankedPaper

# DTOs are unchanged
@dataclass
class VoteDTO: direction: str
@dataclass
class TagDTO: tag: str

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
    year_or_date: str | None
    upvotes: int
    downvotes: int
    tags: List[Dict[str, Any]] = field(default_factory=list)
    category: str | None = None
    replies_data: dict | None = None
    bleeding_edge_score: float | None = None
    recency_component: float | None = None
    reputation_component: float | None = None
    popularity_component: float | None = None
    
    @classmethod
    def _build_unified_tags(cls, paper: Paper) -> List[Dict[str, Any]]:
        unified_tags = []
        for tag in (paper.keywords or []):
            unified_tags.append({"name": tag, "isRemovable": False})
        for tag in (paper.user_tags or []):
            unified_tags.append({"name": tag, "isRemovable": True})
        return unified_tags

    @classmethod
    def from_ranked_paper(cls, ranked_paper: RankedPaper) -> "PaperDTO":
        paper = ranked_paper.paper
        year_or_date_str = paper.year_or_date.isoformat() if paper.year_or_date else None
        return cls(
            id=paper.id,
            source=paper.source,
            source_id=paper.source_id,
            title=paper.title,
            authors=[author.get('name', 'Unknown Author') for author in (paper.authors or [])],
            abstract=paper.abstract,
            paper_url=paper.paper_url,
            pdf_url=paper.pdf_url,
            venue_or_category=paper.venue_or_category,
            year_or_date=year_or_date_str,
            upvotes=paper.upvotes,
            downvotes=paper.downvotes,
            tags=cls._build_unified_tags(paper),
            category=paper.category,
            replies_data=paper.replies_data,
            bleeding_edge_score=ranked_paper.bleeding_edge_score,
            recency_component=ranked_paper.recency_component,
            reputation_component=ranked_paper.reputation_component,
            popularity_component=ranked_paper.popularity_component
        )

    @classmethod
    def from_model(cls, model: Paper) -> "PaperDTO":
        year_or_date_str = model.year_or_date.isoformat() if model.year_or_date else None
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
            year_or_date=year_or_date_str,
            upvotes=model.upvotes,
            downvotes=model.downvotes,
            tags=cls._build_unified_tags(model),
            category=model.category,
            replies_data=model.replies_data
        )

class PaperController(Controller):
    path = "/api/papers"

    @get("/{paper_id:int}")
    async def get_paper(self, session: AsyncSession, paper_id: int) -> Response[PaperDTO] | PaperDTO:
        paper = await paper_repository.get_paper_by_id(session, paper_id)
        if not paper:
            return Response(status_code=status_codes.HTTP_404_NOT_FOUND, content={"error": "Paper not found"})
        return PaperDTO.from_model(paper)
    
    @post("/{paper_id:int}/tags")
    async def add_tag(self, session: AsyncSession, paper_id: int, data: TagDTO) -> Response[None]:
        result = await paper_repository.add_user_tag(session, paper_id, data.tag)
        if result == 'NOT_FOUND': return Response(status_code=status_codes.HTTP_404_NOT_FOUND, content={"error": "Paper not found"})
        if result == 'FULL': return Response(status_code=status_codes.HTTP_409_CONFLICT, content={"error": "Tag limit reached"})
        if result == 'EXISTS': return Response(status_code=status_codes.HTTP_409_CONFLICT, content={"error": "Tag already exists"})
        return Response(status_code=status_codes.HTTP_201_CREATED)

    @delete("/{paper_id:int}/tags")
    async def remove_tag(self, session: AsyncSession, paper_id: int, data: TagDTO) -> Response[None]:
        result = await paper_repository.remove_user_tag(session, paper_id, data.tag)
        if result == 'NOT_FOUND' or result == 'TAG_NOT_FOUND': return Response(status_code=status_codes.HTTP_404_NOT_FOUND, content={"error": "Resource not found"})
        return Response(status_code=status_codes.HTTP_204_NO_CONTENT)

    # --- THIS IS THE FIX ---
    # The `status_code=204` has been removed from the decorator.
    # Litestar will now correctly use 204 for the `return None` success case,
    # and 400/404 for the `Response` error cases.
    @post("/{paper_id:int}/vote")
    async def vote_on_paper(self, session: AsyncSession, paper_id: int, data: VoteDTO) -> Response[None] | None:
        if data.direction not in ['up', 'down']:
            return Response(status_code=status_codes.HTTP_400_BAD_REQUEST, content={"error": "Invalid vote direction"})
        success = await paper_repository.vote_on_paper(session, paper_id, data.direction)
        if not success:
            return Response(status_code=status_codes.HTTP_404_NOT_FOUND, content={"error": "Paper not found"})
        return None

    @get("/arxiv")
    async def list_arxiv_papers(self, session: AsyncSession, limit: int = 50, offset: int = 0, tags: str | None = None) -> List[PaperDTO]:
        tags_list = tags.split(',') if tags else None
        ranked_papers = await ranking_service.get_ranked_arxiv_papers(session, limit=limit, offset=offset, tags=tags_list)
        return [PaperDTO.from_ranked_paper(rp) for rp in ranked_papers]

    @get("/openreview")
    async def list_openreview_papers(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        tags: str | None = None,
        venue: str | None = None,
        year: int | None = None,
        category: str | None = None,
    ) -> List[PaperDTO]:
        tags_list = tags.split(',') if tags else None
        ranked_papers = await ranking_service.get_ranked_openreview_papers(
            session,
            limit=limit,
            offset=offset,
            tags=tags_list,
            venue=venue,
            year=year,
            category=category,
        )
        return [PaperDTO.from_ranked_paper(rp) for rp in ranked_papers]