# File: backend/controller/comment_controller.py

from litestar import Controller, get, post
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from dataclasses import dataclass
from datetime import datetime

from model.comment import Comment
from model.comment_repository import comment_repository

@dataclass
class CommentCreateDTO:
    body: str

@dataclass
class CommentReadDTO:
    id: int
    body: str
    created_at: datetime
    author_name: str = "Anonymous"

    @classmethod
    def from_model(cls, model: Comment) -> "CommentReadDTO":
        return cls(id=model.id, body=model.body, created_at=model.created_at)

class CommentController(Controller):
    path = "/api" # Base path

    @get("/papers/{paper_id:int}/comments")
    async def list_comments_for_paper(self, session: AsyncSession, paper_id: int) -> List[CommentReadDTO]:
        db_comments = await comment_repository.get_comments_for_paper(session, paper_id)
        return [CommentReadDTO.from_model(comment) for comment in db_comments]

    @post("/papers/{paper_id:int}/comments", status_code=201)
    async def create_comment_for_paper(self, session: AsyncSession, paper_id: int, data: CommentCreateDTO) -> CommentReadDTO:
        new_comment = await comment_repository.create_comment(session, paper_id, data.body)
        return CommentReadDTO.from_model(new_comment)