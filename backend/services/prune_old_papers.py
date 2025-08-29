# File: backend/services/prune_old_papers.py

import asyncio
import logging
from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import delete

from model.database import SessionMaker
from model.paper import Paper
from services.config import PAPER_SHELF_LIFE_MONTHS, LOGGING_CONFIG

logging.basicConfig(**LOGGING_CONFIG)

async def prune_papers():
    """
    Deletes papers from the database that are older than the configured shelf life.
    """
    logging.info("Starting the paper pruning process...")

    cutoff_date = date.today() - relativedelta(months=PAPER_SHELF_LIFE_MONTHS)
    logging.info(f"Calculated cutoff date: All papers before {cutoff_date} will be pruned.")
    
    async with SessionMaker() as session:
        try:
            stmt = (
                delete(Paper)
                .where(Paper.source == 'arxiv')
                # This direct date comparison is clean and efficient.
                .where(Paper.year_or_date < cutoff_date)
            )
            
            result = await session.execute(stmt)
            await session.commit()
            
            logging.info(f"✅ Pruning complete. Deleted {result.rowcount} old papers.")

        except Exception as e:
            await session.rollback()
            logging.error(f"❌ An error occurred during pruning: {e}", exc_info=True)
            raise