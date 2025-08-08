from litestar import Litestar
from litestar.di import Provide
from model.database import SessionMaker
from controller.paper_controller import PaperController
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator # <-- IMPORT THIS

# Dependency function to provide a DB session
# UPDATE THE RETURN TYPE HINT HERE
async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionMaker() as session:
        yield session

# Main application instance (no changes here)
app = Litestar(
    route_handlers=[PaperController],
    dependencies={"session": Provide(provide_db_session)}
)