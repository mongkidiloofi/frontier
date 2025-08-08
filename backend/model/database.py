# in model/database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Standard asyncpg driver, no extra arguments
DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

engine = create_async_engine(DATABASE_URL)

SessionMaker = async_sessionmaker(engine, expire_on_commit=False)