import httpx
import asyncio
import os
from typing import Dict, List
from .reputation_config import ALL_VENUE_VARIATIONS

SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1"
API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
HEADERS = {"x-api-key": API_KEY} if API_KEY else {}

class SemanticScholarService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=20.0, headers=HEADERS)
        print("Initializing Semantic Scholar Service...")

    async def get_author_publication_score(self, author_name: str) -> int:
        author_search_url = f"{SEMANTIC_SCHOLAR_API_URL}/author/search"
        search_params = {"query": author_name, "fields": "papers.venue", "limit": 1}
        
        try:
            response = await self.client.get(author_search_url, params=search_params)
            response.raise_for_status()
            search_results = response.json()

            if not search_results.get("data"):
                return 0
            
            top_author_result = search_results["data"][0]
            publication_count = 0
            if top_author_result.get("papers"):
                for paper in top_author_result["papers"]:
                    if paper and paper.get("venue"):
                        venue = paper["venue"].lower()
                        if any(variation in venue for variation in ALL_VENUE_VARIATIONS):
                            publication_count += 1
            
            if publication_count > 0:
                print(f"  -> Reputation: Found {publication_count} top-tier pubs for '{author_name}'")
            return publication_count

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                print(f"  -> WARN: Rate limit hit for '{author_name}'. Backing off.")
                await asyncio.sleep(10)
            else:
                print(f"  -> API Error for '{author_name}': {e.response.status_code}")
            return 0
        except Exception as e:
            print(f"  -> Unexpected S2 Service Error for '{author_name}': {e}")
            return 0

    async def calculate_paper_score(self, authors: List[Dict]) -> float:
        total_score = 0.0
        processed_authors = set()

        for author_data in authors:
            author_name = author_data.get("name")
            if author_name and author_name not in processed_authors:
                # Use a shorter sleep if you have an API key, longer if not.
                await asyncio.sleep(1.1 if API_KEY else 3.1) 
                author_score = await self.get_author_publication_score(author_name)
                total_score += author_score
                processed_authors.add(author_name)
        
        return total_score

semantic_scholar_service = SemanticScholarService()