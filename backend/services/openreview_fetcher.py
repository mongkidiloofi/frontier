# File: backend/services/openreview_fetcher.py
"""
This service fetches paper data from the OpenReview API. It is designed to be
run as a standalone script (e.g., via a cron job).

The fetcher uses a hybrid sync strategy defined in the config file:
- 'full_sync': Fetches all papers for a venue. Ideal for annual conferences.
- 'incremental_sync': Uses a high-water mark to fetch only new papers. Ideal
  for continuously publishing journals like TMLR.

To run this script directly for testing:
1. Ensure your .env file is populated with database and OpenReview credentials.
2. Run the command: python -m services.openreview_fetcher
"""

import asyncio
import logging
import openreview.api
import openreview
import os
import datetime
from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError

# --- Project Imports ---
from model.database import SessionMaker
from model.paper import Paper
from model.job_tracker import JobTracker
from services.config import (
    LOGGING_CONFIG, DB_COMMIT_BATCH_SIZE, BASE_VENUE_CONFIGS,
    OPENREVIEW_API_PAGE_SIZE, OPENREVIEW_MAX_FETCH_ATTEMPTS
)

CONFERENCE_FETCH_START_YEAR = 2024
logging.basicConfig(**LOGGING_CONFIG)

class OpenReviewFetcher:
    def __init__(self):
        or_user = os.getenv("OPENREVIEW_USER")
        or_pass = os.getenv("OPENREVIEW_PASS")
        if not or_user or not or_pass:
            raise ValueError("OPENREVIEW_USER and OPENREVIEW_PASS must be set in .env file.")
        self.client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net', username=or_user, password=or_pass)
        logging.info("Initialized OpenReview API V2 client.")

    def _generate_full_venue_list(self) -> list:
        full_list, current_year = [], datetime.datetime.now().year
        for config in BASE_VENUE_CONFIGS:
            if config['type'] == 'conference':
                for year in range(CONFERENCE_FETCH_START_YEAR, current_year + 1):
                    venueid = config['venueid_pattern'].format(base=config['name_prefix'], year=year)
                    full_list.append({**config, 'name': f"{config['display_name']} {year}", 'venueid': venueid})
            elif config['type'] == 'journal':
                full_list.append({**config, 'name': config['display_name'], 'venueid': config['venueid_pattern']})
        logging.info(f"Generated {len(full_list)} venues to process for years {CONFERENCE_FETCH_START_YEAR}-{current_year}.")
        return full_list

    async def get_journal_high_water_mark(self, journal_name: str) -> str | None:
        """Retrieves the last processed paper ID for a given journal."""
        job_name = f"openreview_fetcher_{journal_name}"
        async with SessionMaker() as session:
            stmt = select(JobTracker.last_processed_marker).where(JobTracker.job_name == job_name)
            result = await session.execute(stmt)
            return result.scalars().first()

    async def update_journal_high_water_mark(self, journal_name: str, new_marker_id: str):
        """Updates the high-water mark for a given journal."""
        job_name = f"openreview_fetcher_{journal_name}"
        async with SessionMaker() as session:
            try:
                result = await session.execute(select(JobTracker).where(JobTracker.job_name == job_name))
                if result.scalars().first():
                    await session.execute(update(JobTracker).where(JobTracker.job_name == job_name).values(last_processed_marker=new_marker_id))
                else:
                    session.add(JobTracker(job_name=job_name, last_processed_marker=new_marker_id))
                await session.commit()
                logging.info(f"Updated high-water mark for {journal_name} to: {new_marker_id}")
            except Exception as e:
                await session.rollback()
                logging.error(f"Failed to update high-water mark for {journal_name}: {e}", exc_info=True)
                raise

    def _find_paper_category(self, note_content: dict) -> str | None:
        """Intelligently searches for the paper's category in multiple common locations."""
        venue_string = note_content.get('venue', {}).get('value', '').lower()
        if 'oral' in venue_string: return 'Oral'
        if 'spotlight' in venue_string: return 'Spotlight'
        if 'poster' in venue_string: return 'Poster'
        certifications = note_content.get('certifications', {}).get('value', [])
        for cert in certifications:
            if 'certification' in cert.lower(): return cert
        return None

    def _sanitize_string(self, text: str | None) -> str | None:
        if text is None: return None
        return text.replace('\0', '')

    def _get_publication_date(self, note, config) -> datetime.date:
        if note.pdate:
            return datetime.datetime.fromtimestamp(note.pdate / 1000).date()
        try:
            year_str = config['name'].split()[-1]
            year = int(year_str)
            return datetime.date(year, 1, 1)
        except (ValueError, IndexError):
            return datetime.date.today()

    def _parse_note_to_paper(self, note, config):
        note_content = note.content
        raw_title = note_content.get('title', {}).get('value')
        raw_authors_list = note_content.get('authors', {}).get('value')
        if not raw_title or not raw_authors_list: return None

        title = self._sanitize_string(raw_title)
        authors_list = [{'name': self._sanitize_string(author)} for author in raw_authors_list]
        abstract = self._sanitize_string(note_content.get('abstract', {}).get('value'))
        
        raw_keywords_value = note_content.get('keywords', {}).get('value')
        initial_keywords = []
        if isinstance(raw_keywords_value, str):
            initial_keywords = [raw_keywords_value]
        elif isinstance(raw_keywords_value, list):
            initial_keywords = raw_keywords_value
        
        final_keywords = []
        for item in initial_keywords:
            if not isinstance(item, str): continue
            normalized_item = item.replace(';', ',')
            split_items = [tag.strip() for tag in normalized_item.split(',')]
            final_keywords.extend(split_items)
        
        keywords = [self._sanitize_string(kw).lower() for kw in final_keywords if self._sanitize_string(kw)]
        
        category = self._find_paper_category(note_content)

        return Paper(
            source='openreview', source_id=note.id, title=title,
            authors=authors_list, abstract=abstract,
            paper_url=f"https://openreview.net/forum?id={note.id}",
            pdf_url=f"https://openreview.net{note_content.get('pdf',{}).get('value')}" if note_content.get('pdf') else None,
            venue_or_category=config['name'],
            year_or_date=self._get_publication_date(note, config),
            keywords=keywords,
            category=category.title() if category else None,
            reputation_score=0.0
        )

    async def _fetch_all_pages_for_venue(self, config: dict) -> list:
        all_notes, offset = [], 0
        while True:
            logging.info(f"Fetching papers for '{config['name']}' with offset {offset}...")
            query_params = { 'limit': OPENREVIEW_API_PAGE_SIZE, 'offset': offset, 'sort': 'pdate:desc', 'content': {'venueid': config['venueid']} }
            try:
                notes_batch = await asyncio.to_thread(self.client.get_notes, **query_params)
                if not notes_batch or len(notes_batch) == 0:
                    logging.info(f"Finished fetching all pages for '{config['name']}'. Total found: {len(all_notes)}"); break
                all_notes.extend(notes_batch); offset += len(notes_batch)
            except openreview.OpenReviewException as e:
                logging.error(f"API error during pagination for '{config['name']}': {e}. Stopping fetch for this venue."); break
        return all_notes

    async def _process_and_commit_notes(self, new_notes: list, config: dict):
        logging.info(f"Processing and committing {len(new_notes)} new papers for '{config['name']}'...")
        papers_to_commit = [p for p in [self._parse_note_to_paper(note, config) for note in new_notes] if p is not None]
        for i in range(0, len(papers_to_commit), DB_COMMIT_BATCH_SIZE):
            batch = papers_to_commit[i:i + DB_COMMIT_BATCH_SIZE]
            logging.info(f"Committing batch of {len(batch)} papers for {config['name']}...")
            async with SessionMaker() as commit_session:
                try:
                    commit_session.add_all(batch)
                    await commit_session.commit()
                except Exception as e:
                    await commit_session.rollback()
                    logging.error(f"Database commit failed for batch. Error: {e}", exc_info=True)
        logging.info(f"Finished committing all papers for '{config['name']}'.")
    
    async def _handle_new_notes(self, notes: list, config: dict):
        logging.info(f"Found {len(notes)} potential papers for '{config['name']}'. Checking for duplicates...")
        or_ids = {note.id for note in notes if not note.replyto}
        if not or_ids: logging.info("No top-level notes found in the fetched batch."); return
        async with SessionMaker() as session:
            stmt = select(Paper.source_id).where(Paper.source_id.in_(or_ids))
            result = await session.execute(stmt)
            existing_ids = {row[0] for row in result.all()}
        new_notes = [note for note in notes if note.id in or_ids and note.id not in existing_ids]
        if not new_notes: logging.info(f"No new papers to add for '{config['name']}'."); return
        await self._process_and_commit_notes(new_notes, config)

    async def _full_sync_venue(self, config):
        all_notes = await self._fetch_all_pages_for_venue(config)
        if not all_notes: logging.info(f"No papers found for venue '{config['name']}'."); return
        await self._handle_new_notes(all_notes, config)

    async def _incremental_sync_journal(self, config):
        journal_name = config['display_name']
        high_water_mark = await self.get_journal_high_water_mark(journal_name)
        logging.info(f"Journal: {journal_name}, Existing high-water mark: {high_water_mark}")
        papers_found = []
        if high_water_mark is None:
            logging.warning(f"No high-water mark for {journal_name}. Performing initial full backfill.")
            papers_found = await self._fetch_all_pages_for_venue(config)
        else:
            logging.info(f"Fetching new papers for {journal_name} since mark: {high_water_mark}")
            offset, found_mark, pages_checked = 0, False, 0
            while not found_mark and pages_checked < OPENREVIEW_MAX_FETCH_ATTEMPTS:
                logging.info(f"Page {pages_checked + 1}: Fetching papers for {journal_name} with offset {offset}...")
                notes_batch = await self._fetch_all_pages_for_venue(config)
                if not notes_batch: logging.warning(f"Could not find high-water mark for {journal_name} but reached end of history."); break
                for note in notes_batch:
                    if note.id == high_water_mark: found_mark = True; break
                    papers_found.append(note)
                if not found_mark: offset += len(notes_batch); pages_checked += 1
            if not found_mark and pages_checked >= OPENREVIEW_MAX_FETCH_ATTEMPTS:
                 logging.error(f"High-water mark not found for {journal_name} after checking {pages_checked} pages. Aborting sync."); return
        if not papers_found: logging.info(f"No new papers to process for {journal_name}."); return
        new_high_water_mark = papers_found[0].id
        try:
            await self._handle_new_notes(papers_found, config)
        except Exception as e:
            logging.error(f"Failed to process papers for {journal_name}, but will still update high-water mark. Error: {e}", exc_info=True)
        await self.update_journal_high_water_mark(journal_name, new_high_water_mark)

    async def _sync_venue(self, config):
        strategy = config.get('sync_strategy', 'full_sync')
        logging.info(f"--- Processing venue: {config['name']} (Strategy: {strategy}) ---")
        try:
            if strategy == 'incremental_sync':
                await self._incremental_sync_journal(config)
            else:
                await self._full_sync_venue(config)
        except Exception as e:
            logging.error(f"❌ Unexpected critical error processing venue '{config['name']}': {e}", exc_info=True)

    async def run(self):
        logging.info("--- Starting OpenReview Hybrid Sync Run ---")
        venues_to_process = self._generate_full_venue_list()
        for config in venues_to_process:
            await self._sync_venue(config)
        logging.info("--- ✅ All venue syncs complete. ---")


if __name__ == "__main__":
    fetcher = OpenReviewFetcher()
    asyncio.run(fetcher.run())