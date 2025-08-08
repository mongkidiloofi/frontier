import asyncio
from model.database import engine, Base
from model.arxiv_paper import ArxivPaper # Import your model

async def create_db_and_tables():
    async with engine.begin() as conn:
        # This deletes the old table if it exists, ensuring a fresh start
        await conn.run_sync(Base.metadata.drop_all)
        # This creates the new table based on your ArxivPaper model
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("✅ Tables recreated successfully in the database.")

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())