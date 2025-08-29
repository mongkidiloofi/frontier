# File: backend/model/paper_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.dialects.postgresql import array # --- ADDED ---
from typing import List

from .paper import Paper

class PaperRepository:
    # --- ADDED: A new method to get a single paper by its primary key ---
    async def get_paper_by_id(self, session: AsyncSession, paper_id: int) -> Paper | None:
        """Retrieves a single paper by its integer ID."""
        stmt = select(Paper).where(Paper.id == paper_id)
        result = await session.execute(stmt)
        return result.scalars().first()
    
    # --- ADDED: Method to add a user tag atomically ---
    async def add_user_tag(self, session: AsyncSession, paper_id: int, tag: str) -> str:
        """
        Adds a tag to a paper's user_tags list.
        Returns 'SUCCESS', 'FULL', 'EXISTS', or 'NOT_FOUND'.
        Uses row-level locking to prevent race conditions.
        """
        # Lock the row for the duration of the transaction to ensure atomicity
        stmt = select(Paper).where(Paper.id == paper_id).with_for_update()
        result = await session.execute(stmt)
        paper = result.scalars().first()

        if not paper:
            return 'NOT_FOUND'

        current_tags = paper.user_tags or []
        if tag in current_tags:
            return 'EXISTS'
        
        if len(current_tags) >= 3:
            return 'FULL'

        paper.user_tags = current_tags + [tag]
        await session.commit()
        return 'SUCCESS'

    # --- ADDED: Method to remove a user tag atomically ---
    async def remove_user_tag(self, session: AsyncSession, paper_id: int, tag: str) -> str:
        """
        Removes a tag from a paper's user_tags list.
        Returns 'SUCCESS', 'NOT_FOUND', or 'TAG_NOT_FOUND'.
        """
        stmt = select(Paper).where(Paper.id == paper_id).with_for_update()
        result = await session.execute(stmt)
        paper = result.scalars().first()

        if not paper:
            return 'NOT_FOUND'

        current_tags = paper.user_tags or []
        if tag not in current_tags:
            return 'TAG_NOT_FOUND'
        
        paper.user_tags = [t for t in current_tags if t != tag]
        await session.commit()
        return 'SUCCESS'

    # --- (vote_on_paper and other methods are unchanged) ---
    async def vote_on_paper(self, session: AsyncSession, paper_id: int, direction: str) -> bool:
        if direction not in ['up', 'down']: raise ValueError("Direction must be 'up' or 'down'")
        column_to_increment = Paper.upvotes if direction == 'up' else Paper.downvotes
        stmt = update(Paper).where(Paper.id == paper_id).values({column_to_increment: column_to_increment + 1}).execution_options(synchronize_session="fetch")
        result = await session.execute(stmt); await session.commit(); return result.rowcount > 0
    async def get_recent_openreview_papers(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        tags: List[str] | None = None,
        venue: str | None = None,
        year: int | None = None,
        category: str | None = None,
    ) -> List[Paper]:
        # This logic was already correct: filter first, then order and paginate.
        query = select(Paper).where(Paper.source == 'openreview')

        if tags:
            query = query.where(Paper.keywords.contains(tags))
        if venue:
            query = query.where(Paper.venue_or_category.startswith(venue))
        if year:
            query = query.where(func.extract('year', Paper.year_or_date) == year)
        if category:
            query = query.where(Paper.category == category)

        query = query.order_by(Paper.year_or_date.desc(), Paper.id.desc()).offset(offset).limit(limit)
        
        result = await session.execute(query)
        return result.scalars().all()

    async def get_arxiv_papers(self, session: AsyncSession, limit: int = 50, offset: int = 0, tags: List[str] | None = None) -> List[Paper]:
        query = select(Paper).where(Paper.source == 'arxiv')
        if tags: query = query.where(Paper.keywords.contains(tags))
        query = query.order_by(Paper.year_or_date.desc()).offset(offset).limit(limit)
        result = await session.execute(query); return result.scalars().all()

paper_repository = PaperRepository()