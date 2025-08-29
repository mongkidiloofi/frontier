# File: backend/model/comment_repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from .comment import Comment

class CommentRepository:
    async def create_comment(self, session: AsyncSession, paper_id: int, body: str) -> Comment:
        """Creates and saves a new anonymous comment for a paper."""
        new_comment = Comment(paper_id=paper_id, body=body)
        session.add(new_comment)
        await session.commit()
        await session.refresh(new_comment)
        return new_comment

    async def get_comments_for_paper(self, session: AsyncSession, paper_id: int) -> List[Comment]:
        """Retrieves all comments for a given paper, sorted chronologically (newest first)."""
        stmt = (
            select(Comment)
            .where(Comment.paper_id == paper_id)
            .order_by(Comment.created_at.desc())
        )
        result = await session.execute(stmt)
        return result.scalars().all()

comment_repository = CommentRepository()