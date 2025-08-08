from litestar.config.cors import CORSConfig
from litestar import Litestar
from litestar.di import Provide
from model.database import SessionMaker
from controller.paper_controller import PaperController
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator # <-- IMPORT THIS

cors_config = CORSConfig(allow_origins=["http://localhost:5173"])

# Dependency function to provide a DB session
# UPDATE THE RETURN TYPE HINT HERE
async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionMaker() as session:
        yield session

# Main application instance (no changes here)
# Ensure your app definition looks like this:
app = Litestar(
    route_handlers=[PaperController],
    dependencies={"session": Provide(provide_db_session)},
    cors_config=cors_config  # <--- THIS LINE IS CRUCIAL
)