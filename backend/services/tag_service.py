import asyncio
import time
from sqlalchemy import select, text
from typing import List, Set

from model.database import SessionMaker

# --- Caching Configuration ---
CACHE_TTL_SECONDS = 600  # Cache the tag list for 10 minutes

class TagService:
    def __init__(self):
        self._cache: List[str] = []
        self._cache_expiry: float = 0
        self._lock = asyncio.Lock() # Prevents race conditions during cache refresh

    async def get_all_tags(self) -> List[str]:
        """
        Returns a cached list of all unique, sorted tags.
        If the cache is stale, it triggers a database refresh.
        """
        async with self._lock:
            if time.time() > self._cache_expiry:
                await self._refresh_cache()
            return self._cache

    async def _refresh_cache(self):
        """
        Performs an efficient database query to get all unique tags,
        then updates the in-memory cache.
        """
        print("Refreshing tag cache from database...")
        
        # --- THIS IS THE FIX ---
        # This single query is vastly more efficient than fetching all rows.
        # It uses jsonb_array_elements_text to un-nest all tags from both JSONB columns,
        # then gets the distinct, non-empty, sorted list directly from the DB.
        query = text("""
            SELECT DISTINCT tag
            FROM (
                SELECT jsonb_array_elements_text(keywords) AS tag FROM papers WHERE jsonb_typeof(keywords) = 'array'
                UNION ALL
                SELECT jsonb_array_elements_text(user_tags) AS tag FROM papers WHERE jsonb_typeof(user_tags) = 'array'
            ) AS all_tags
            WHERE tag IS NOT NULL AND tag != ''
            ORDER BY tag;
        """)

        async with SessionMaker() as session:
            result = await session.execute(query)
            # The result is a list of tuples, so we extract the first element of each.
            all_tags = [row[0] for row in result.all()]

        self._cache = all_tags
        self._cache_expiry = time.time() + CACHE_TTL_SECONDS
        print(f"Cache refreshed. Found {len(self._cache)} unique tags. Next refresh in {CACHE_TTL_SECONDS / 60} minutes.")

# Create a single, reusable instance
tag_service = TagService()