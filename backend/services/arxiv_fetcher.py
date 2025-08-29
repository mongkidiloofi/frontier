"""
This is a hardened version of the ArXiv fetcher, fetching up to 300 papers sequentially
using a combined category query, ensuring consistent order for stack pointer processes.
It uses a paranoid XML parser, respects the ArXiv API ToS with a 3-second delay between
paginated requests, and includes diagnostic logging.

To run this script directly for testing:
1. Ensure your .env file is populated with database credentials.
2. From the `backend` directory, run: python -m services.arxiv_fetcher
"""

import asyncio
import httpx
import logging
import xml.etree.ElementTree as ET
from urllib.parse import urlencode
from datetime import datetime, date
from dataclasses import dataclass, field
from sqlalchemy import select, update
from typing import List, Dict, Set

# --- Project Imports ---
from model.database import SessionMaker
from model.paper import Paper
from model.job_tracker import JobTracker
from services.semantic_scholar_service import semantic_scholar_service
from services.config import (
    ARXIV_CATEGORIES, ARXIV_FETCHER_JOB_NAME, LOGGING_CONFIG, DB_COMMIT_BATCH_SIZE
)

# --- Setup and Constants ---
logging.basicConfig(**LOGGING_CONFIG)
ARXIV_API_BASE_URL = "http://export.arxiv.org/api/query?"
API_PAGE_SIZE = 100
TARGET_FETCH_SIZE = 50
API_DELAY_SECONDS = 3.0
DEBUG_FILE_NAME = "arxiv_debug.xml"

@dataclass
class ArxivResult:
    entry_id: str
    title: str
    summary: str
    published: datetime
    authors: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    pdf_url: str | None = None

class ArxivFetcher:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.job_name = ARXIV_FETCHER_JOB_NAME
        if not ARXIV_CATEGORIES:
            raise ValueError("ARXIV_CATEGORIES in config.py must not be empty.")
        if DB_COMMIT_BATCH_SIZE <= 0:
            raise ValueError("DB_COMMIT_BATCH_SIZE must be positive.")

    def _parse_xml_entry(self, entry: ET.Element, ns: Dict[str, str]) -> ArxivResult | None:
        try:
            id_el = entry.find('atom:id', ns)
            title_el = entry.find('atom:title', ns)
            if id_el is None or id_el.text is None or title_el is None or title_el.text is None:
                logging.warning("Skipping entry: missing required 'id' or 'title' element.")
                return None
            
            entry_id = id_el.text.split('/')[-1]
            title = title_el.text.strip().replace('\n', ' ').replace('  ', ' ')

            summary_el = entry.find('atom:summary', ns)
            summary = summary_el.text.strip().replace('\n', ' ') if summary_el is not None and summary_el.text is not None else ""

            published_el = entry.find('atom:published', ns)
            published_str = published_el.text if published_el is not None and published_el.text is not None else datetime.utcnow().isoformat() + "Z"
            try:
                published_date = datetime.strptime(published_str, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError as e:
                logging.error(f"Failed to parse published date {published_str} for entry {entry_id}: {e}")
                published_date = datetime.utcnow()
            
            pdf_link_el = entry.find('atom:link[@title="pdf"]', ns)
            pdf_url = pdf_link_el.get('href') if pdf_link_el is not None else None
            
            authors = [name_el.text for author_el in entry.findall('atom:author', ns) if (name_el := author_el.find('atom:name', ns)) is not None and name_el.text is not None]
            categories = [cat.get('term') for cat in entry.findall('atom:category', ns) if cat.get('term')]

            return ArxivResult(
                entry_id=entry_id, title=title, summary=summary, published=published_date,
                authors=authors, categories=categories, pdf_url=pdf_url
            )
        except Exception as e:
            entry_id_for_log = id_el.text if id_el is not None and id_el.text is not None else "ID_UNKNOWN"
            logging.error(f"CRITICAL PARSE ERROR for entry {entry_id_for_log}. Skipping. Error: {e}", exc_info=False)
            return None

    async def _fetch_with_retry(self, url: str, retries: int = 3, backoff: float = 1.0) -> httpx.Response:
        for attempt in range(retries):
            try:
                response = await self.client.get(url, follow_redirects=True)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt == retries - 1:
                    logging.error(f"Failed to fetch after {retries} attempts: {e}", exc_info=True)
                    raise
                await asyncio.sleep(backoff * (2 ** attempt))
        raise Exception("Unexpected retry failure")

    async def _fetch_paginated_results(self, search_query: str, total_to_fetch: int) -> List[ArxivResult]:
        all_results = []
        for start_index in range(0, total_to_fetch, API_PAGE_SIZE):
            if start_index > 0:
                await asyncio.sleep(API_DELAY_SECONDS)
            chunk_size = min(API_PAGE_SIZE, total_to_fetch - len(all_results))
            if chunk_size <= 0:
                break
            params = { 'search_query': search_query, 'start': start_index, 'max_results': chunk_size, 'sortBy': 'submittedDate', 'sortOrder': 'descending' }
            url = ARXIV_API_BASE_URL + urlencode(params)
            
            try:
                response = await self._fetch_with_retry(url)
                namespace = {'atom': 'http://www.w3.org/2005/Atom'}
                root = ET.fromstring(response.content)
                all_entries = root.findall('atom:entry', namespace)
                parsed_entries = [self._parse_xml_entry(entry, namespace) for entry in all_entries]
                successful_parses = [p for p in parsed_entries if p is not None]
                if len(successful_parses) < len(all_entries):
                    logging.warning(f"Parsed {len(successful_parses)}/{len(all_entries)} entries successfully.")
                all_results.extend(successful_parses)
                if len(all_entries) == 0 and all_results:
                    logging.info("No more entries returned by API. Stopping fetch.")
                    break
                if len(all_entries) < chunk_size:
                    logging.warning(f"Received fewer entries ({len(all_entries)}) than requested ({chunk_size}).")
                    with open(DEBUG_FILE_NAME, 'wb') as f:
                        f.write(response.content)
            except Exception as e:
                logging.error(f"Failed to fetch for query {search_query}: {e}", exc_info=True)
                break
        
        return all_results[:total_to_fetch]

    async def get_high_water_mark(self) -> str | None:
        async with SessionMaker() as session:
            stmt = select(JobTracker.last_processed_marker).where(JobTracker.job_name == self.job_name)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def update_high_water_mark(self, new_marker_id: str):
        async with SessionMaker() as session:
            try:
                result = await session.execute(select(JobTracker).where(JobTracker.job_name == self.job_name))
                if result.scalars().first():
                    await session.execute(update(JobTracker).where(JobTracker.job_name == self.job_name).values(last_processed_marker=new_marker_id))
                else:
                    session.add(JobTracker(job_name=self.job_name, last_processed_marker=new_marker_id))
                await session.commit()
                logging.info(f"Updated high-water mark to: {new_marker_id}")
            except Exception as e:
                await session.rollback()
                logging.error(f"Failed to update high-water mark: {e}", exc_info=True)
                raise

    async def _check_duplicates(self, session, ids: Set[str]) -> Set[str]:
        batch_size = 100
        existing = set()
        for i in range(0, len(ids), batch_size):
            batch_ids = list(ids)[i:i + batch_size]
            res = await session.execute(select(Paper.source_id).where(Paper.source_id.in_(batch_ids)))
            existing.update(row[0] for row in res.all())
        return existing

    async def _process_and_commit_in_batches(self, papers_to_process: List[ArxivResult]):
        logging.info(f"Processing and committing {len(papers_to_process)} papers in batches of {DB_COMMIT_BATCH_SIZE}...")
        total_success, total_failure = 0, 0
        async with SessionMaker() as session:
            for i in range(0, len(papers_to_process), DB_COMMIT_BATCH_SIZE):
                batch = papers_to_process[i:i + DB_COMMIT_BATCH_SIZE]
                logging.info(f"--- Processing batch #{i//DB_COMMIT_BATCH_SIZE + 1} ({len(batch)} papers) ---")
                
                ids = {p.entry_id for p in batch}
                existing = await self._check_duplicates(session, ids)
                batch = [p for p in batch if p.entry_id not in existing]
                if not batch:
                    logging.info("No new papers in batch after duplicate check.")
                    continue
                
                async def process_single(result: ArxivResult):
                    try:
                        rep_score = await semantic_scholar_service.calculate_paper_score([{'name': name} for name in result.authors])
                    except Exception as e:
                        logging.warning(f"Failed to calculate reputation score for {result.entry_id}: {e}. Using fallback score 0.")
                        rep_score = 0
                    authors = [{'name': name} for name in result.authors] if result.authors else [{'name': 'Unknown Author'}]
                    # Convert keywords, venue_or_category, and category to lowercase
                    keywords = [cat.lower() for cat in result.categories] if result.categories else ['cs.lg']
                    return Paper(
                        source='arxiv',
                        source_id=result.entry_id,
                        title=result.title,
                        authors=authors,
                        abstract=result.summary,
                        paper_url=f"http://arxiv.org/abs/{result.entry_id}",
                        pdf_url=result.pdf_url,
                        venue_or_category=result.categories[0].lower() if result.categories else 'cs.lg',
                        year_or_date=result.published.date(),
                        category=result.categories[0].lower() if result.categories else None,
                        keywords=keywords,
                        replies_data=None,
                        user_tags=[],
                        reputation_score=rep_score,
                        upvotes=0,
                        downvotes=0
                    )

                processed = await asyncio.gather(*[process_single(p) for p in batch])
                to_commit = [p for p in processed if p]
                
                if to_commit:
                    try:
                        session.add_all(to_commit)
                        await session.commit()
                        total_success += len(to_commit)
                    except Exception as e:
                        await session.rollback()
                        logging.error(f"DB commit failed for batch. Error: {e}", exc_info=True)
                
                total_failure += len(batch) - len(to_commit)
        
        logging.info(f"Processing Summary: Succeeded={total_success}, Failed={total_failure}")

    async def run(self):
        logging.info("--- Starting ArXiv Fetcher Run ---")
        try:
            hwm = await self.get_high_water_mark()
            papers_found, query = [], " OR ".join([f"cat:{cat}" for cat in ARXIV_CATEGORIES])
            
            logging.info(f"Fetching up to {TARGET_FETCH_SIZE} papers with query: {query}")
            papers_found = await self._fetch_paginated_results(query, total_to_fetch=TARGET_FETCH_SIZE)
            if hwm:
                papers_found = [p for p in papers_found if p.entry_id != hwm]
            
            if not papers_found:
                logging.info("No new papers to process.")
                return
            
            logging.info(f"Fetched {len(papers_found)} papers from API.")
            await self._process_and_commit_in_batches(papers_found)
            
            if papers_found:
                await self.update_high_water_mark(papers_found[0].entry_id)

        except Exception as e:
            logging.critical(f"Critical error during fetcher run: {e}", exc_info=True)
        finally:
            await self.client.aclose()
            logging.info("--- ArXiv Fetcher Run Complete ---")

if __name__ == "__main__":
    fetcher = ArxivFetcher()
    asyncio.run(fetcher.run())