# File: backend/create_tables.py

import asyncio
from model.database import Base, engine
from model.paper import Paper
from model.job_tracker import JobTracker
from model.comment import Comment

async def create_all_tables():
    """
    Connects to the database, drops all existing tables, and then creates them anew.
    WARNING: This is a destructive operation and will delete all data in the tables.
    """
    print("Connecting to the database...")
    async with engine.begin() as conn:
        print("Dropping all existing tables...")
        # Drop all tables associated with the metadata
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ All tables dropped successfully.")

        print("Creating all tables from scratch...")
        # This will inspect all imported models that inherit from Base
        # and create the corresponding tables in the database.
        await conn.run_sync(Base.metadata.create_all)
        
    print("✅ All tables re-created successfully.")

if __name__ == "__main__":
    # Adding a simple confirmation prompt to prevent accidental data loss.
    confirm = input("⚠️ WARNING: This will drop all tables and delete all data. Are you sure you want to continue? (y/N): ")
    if confirm.lower() == 'y':
        asyncio.run(create_all_tables())
    else:
        print("Operation cancelled.")