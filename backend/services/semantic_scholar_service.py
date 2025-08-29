import httpx
import asyncio
import os
import logging
from typing import Dict, List

# Import from the single, unified config file
from .config import ALL_VENUE_VARIATIONS, LOGGING_CONFIG

# --- Setup ---
logging.basicConfig(**LOGGING_CONFIG)

SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1"
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
HEADERS = {"x-api-key": API_KEY} if API_KEY else {}
CONCURRENCY_LIMIT = 5
# --- NEW: Retry Configuration ---
# We will try a total of 3 times for each author.
MAX_RETRIES = 3
# The first time we get a rate limit error, we'll wait 5 seconds.
INITIAL_BACKOFF_SECONDS = 5

class SemanticScholarService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=20.0, headers=HEADERS)
        self.semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        logging.info(f"Initializing Semantic Scholar Service with concurrency limit of {CONCURRENCY_LIMIT}.")

    async def get_author_publication_score(self, author_name: str) -> int:
        """
        Fetches the publication score for a single author with a robust retry loop
        to handle transient errors like rate limiting.
        """
        author_search_url = f"{SEMANTIC_SCHOLAR_API_URL}/author/search"
        search_params = {"query": author_name, "fields": "papers.venue", "limit": 1}
        
        # --- NEW: ROBUST RETRY LOOP ---
        for attempt in range(MAX_RETRIES):
            try:
                response = await self.client.get(author_search_url, params=search_params)
                response.raise_for_status() # Raises an exception for 4xx/5xx errors
                
                # If the request was successful, process the data and return immediately.
                search_results = response.json()
                if not search_results.get("data"):
                    return 0 # Author not found is a success, not an error.
                
                top_author_result = search_results["data"][0]
                publication_count = 0
                if top_author_result.get("papers"):
                    for paper in top_author_result["papers"]:
                        if paper and paper.get("venue"):
                            venue = paper["venue"].lower()
                            if any(variation in venue for variation in ALL_VENUE_VARIATIONS):
                                publication_count += 1
                
                if publication_count > 0:
                    logging.debug(f"Reputation: Found {publication_count} top-tier pubs for '{author_name}'")
                return publication_count # Success! Exit the loop and return the score.

            except httpx.HTTPStatusError as e:
                # This block now handles errors that might be temporary.
                if e.response.status_code == 429: # Rate limit error
                    # On failure, calculate an increasing delay (5s, 10s, 20s)
                    backoff_time = INITIAL_BACKOFF_SECONDS * (2 ** attempt)
                    logging.warning(
                        f"Rate limit hit for '{author_name}' (Attempt {attempt + 1}/{MAX_RETRIES}). "
                        f"Backing off for {backoff_time} seconds."
                    )
                    await asyncio.sleep(backoff_time)
                    # The loop will now continue to the next attempt.
                else:
                    # For other HTTP errors (like 500), they are less likely to be temporary.
                    # We log the error and give up immediately.
                    logging.error(f"Non-retryable HTTP Error for '{author_name}': {e.response.status_code}")
                    return 0
            except Exception as e:
                logging.error(f"Unexpected S2 Service Error for '{author_name}': {e}", exc_info=False)
                return 0 # Give up on other unexpected errors.
        
        # This code is only reached if the `for` loop finishes without a successful return.
        logging.error(f"Failed to get score for '{author_name}' after {MAX_RETRIES} attempts.")
        return 0
        # --- END OF RETRY LOGIC ---

    async def _get_score_with_semaphore(self, author_name: str) -> int:
        """
        A private wrapper method that acquires the semaphore before calling the main score method.
        This ensures that we never exceed our concurrency limit.
        """
        async with self.semaphore:
            await asyncio.sleep(0.5) 
            return await self.get_author_publication_score(author_name)

    async def calculate_paper_score(self, authors: List[Dict]) -> float:
        """
        Calculates the total reputation score for a paper by fetching all its authors'
        scores concurrently and summing them up.
        """
        unique_author_names = {author_data.get("name") for author_data in authors if author_data.get("name")}
        
        if not unique_author_names:
            return 0.0

        tasks = [self._get_score_with_semaphore(name) for name in unique_author_names]
        
        scores = await asyncio.gather(*tasks)
        
        total_score = sum(scores)
        return float(total_score)

# Create a single, reusable instance of the service
semantic_scholar_service = SemanticScholarService()