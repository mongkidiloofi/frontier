import asyncio
from model.database import engine, Base
# --- THE FIX IS HERE ---
# We now import the single, unified 'Paper' model from 'model/paper.py'.
from model.paper import Paper
# --- END OF FIX ---

async def create_db_and_tables():
    async with engine.begin() as conn:
        print("Dropping all existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating new tables based on models...")
        # Base.metadata knows about the 'papers' table because we imported the Paper class.
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("✅ Tables recreated successfully in the database.")

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())