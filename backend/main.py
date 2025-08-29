# File: backend/main.py

from litestar.config.cors import CORSConfig
from litestar import Litestar
from litestar.di import Provide
from model.database import SessionMaker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from controller.paper_controller import PaperController
from controller.comment_controller import CommentController # <-- IMPORT
from controller.tag_controller import TagController

cors_config = CORSConfig(allow_origins=["http://localhost:5173"])

async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionMaker() as session:
        yield session

app = Litestar(
    route_handlers=[PaperController, CommentController, TagController], # <-- REGISTER
    dependencies={"session": Provide(provide_db_session)},
    cors_config=cors_config
)