# File: backend/model/job_tracker.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class JobTracker(Base):
    """
    Tracks the state of long-running jobs.
    For the arxiv_fetcher, this stores the ID of the last successfully fetched paper.
    """
    __tablename__ = "job_tracker"
    
    job_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    # This now correctly stores a string ID (our high-water mark)
    last_processed_marker: Mapped[str] = mapped_column(String(100))