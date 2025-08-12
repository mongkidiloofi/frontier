import openreview.api
import os
import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from model.paper import Paper

# --- SETUP ---
load_dotenv()
USER, PASSWORD, HOST, PORT, DBNAME = os.getenv("user"), os.getenv("password"), os.getenv("host"), os.getenv("port"), os.getenv("dbname")
DATABASE_URL_SYNC = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
engine_sync = create_engine(DATABASE_URL_SYNC)
SessionMakerSync = sessionmaker(engine_sync)
# ---

# --- DYNAMIC VENUE CONFIGURATION ---
# This configuration has been updated with the corrected AISTATS venueid.
BASE_VENUE_CONFIGS = [
    {'name_prefix': 'ICLR.cc', 'display_name': 'ICLR', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference', 'category_logic': 'parse_from_venue_string'},
    {'name_prefix': 'NeurIPS.cc', 'display_name': 'NeurIPS', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference', 'category_logic': 'parse_from_venue_string'},
    {'name_prefix': 'ICML.cc', 'display_name': 'ICML', 'venueid_pattern': 'ICML.cc/{year}/Conference', 'start_year': 2024, 'type': 'conference', 'category_logic': 'parse_from_venue_string'},
    
    # RLC: No category logic, as requested.
    {'name_prefix': 'rl-conference.cc/RLC', 'display_name': 'RLC', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference'},
    
    # CoRL: No category logic, as requested.
    {'name_prefix': 'robot-learning.org/CoRL', 'display_name': 'CoRL', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference'},
    
    # AISTATS: Corrected venueid prefix, uses the same logic as ICLR/NeurIPS.
    {'name_prefix': 'aistats.org/AISTATS', 'display_name': 'AISTATS', 'venueid_pattern': '{base}/{year}/Conference', 'start_year': 2024, 'type': 'conference', 'category_logic': 'parse_from_venue_string'},
    
    # Journals use simple venueids.
    {'name_prefix': 'TMLR', 'display_name': 'TMLR', 'venueid_pattern': 'TMLR', 'type': 'journal', 'category_logic': 'parse_from_direct_field', 'category_field_name': 'certifications'},
    {'name_prefix': 'DMLR', 'display_name': 'DMLR', 'venueid_pattern': 'DMLR', 'type': 'journal', 'category_logic': 'parse_from_direct_field', 'category_field_name': 'certifications'}
]
LIMIT_PER_VENUE = 1
# ---

def generate_full_venue_list():
    """Dynamically creates the full list of venues with the correct venueid."""
    full_list = []
    current_year = datetime.datetime.now().year
    for config in BASE_VENUE_CONFIGS:
        if config['type'] == 'conference':
            for year in range(config['start_year'], current_year + 1):
                venueid = config['venueid_pattern'].format(base=config['name_prefix'], year=year)
                # Use the new 'display_name' for cleaner logging
                full_list.append({**config, 'name': f"{config['display_name']} {year}", 'venueid': venueid})
        elif config['type'] == 'journal':
            full_list.append({**config, 'name': config['display_name'], 'venueid': config['venueid_pattern']})
    return full_list

# --- HELPER FUNCTIONS ---
def find_category_in_replies(replies_data):
    for reply_content in replies_data:
        decision = reply_content.get('decision', {}).get('value') or reply_content.get('recommendation', {}).get('value')
        if decision: return decision
    return None

def find_category_in_venue_string(venue_string):
    if not venue_string: return None
    parts = venue_string.split()
    last_part = parts[-1].lower()
    if last_part in ['oral', 'spotlight', 'poster']: return parts[-1]
    return "Paper"
# ---

def fetch_papers_from_venues():
    or_user, or_pass = os.getenv("OPENREVIEW_USER"), os.getenv("OPENREVIEW_PASS")
    client = openreview.api.OpenReviewClient(baseurl='https://api2.openreview.net', username=or_user, password=or_pass)
    print("Using OpenReview API V2 client...")

    venues_to_process = generate_full_venue_list()
    
    with SessionMakerSync() as session:
        for config in venues_to_process:
            name, venue_id = config['name'], config['venueid']
            category_logic = config.get('category_logic') 
            print(f"\n--- Processing venue: {name} ---")
            
            try:
                query_params = {
                    'limit': LIMIT_PER_VENUE,
                    'sort': 'pdate:desc',
                    'content': {'venueid': venue_id}
                }
                print(f"  -> Fetching latest paper with query: {query_params['content']}")
                notes = client.get_notes(**query_params)

                print(f"  -> Found {len(notes)} paper. Processing...")
                if not notes: continue
                
                papers_to_commit = []
                for note in notes:
                    if note.replyto: continue
                    or_id = note.id
                    if session.execute(select(Paper).where(Paper.source_id == or_id)).first(): continue
                    
                    note_content = note.content
                    title = note_content.get('title', {}).get('value')
                    authors_list = note_content.get('authors', {}).get('value')
                    if not title or not authors_list: continue

                    category, replies_data = None, []

                    if category_logic == 'parse_from_replies':
                        print("  -> Fetching replies to determine category...")
                        all_replies = client.get_all_notes(forum=note.id)
                        for reply_note in all_replies:
                            if reply_note.id == note.id: continue
                            replies_data.append(reply_note.content)
                        category = find_category_in_replies(replies_data)
                    elif category_logic == 'parse_from_venue_string':
                        category = find_category_in_venue_string(note_content.get('venue', {}).get('value'))
                    elif category_logic == 'parse_from_direct_field':
                        field_name = config['category_field_name']
                        raw_cat = note_content.get(field_name, {}).get('value')
                        category = ", ".join(raw_cat) if isinstance(raw_cat, list) else raw_cat
                    
                    keywords = []
                    for field in ['keywords', 'subject_areas', 'primary_area']:
                        found = note_content.get(field, {}).get('value')
                        if found and isinstance(found, list): keywords = found; break

                    year = str(datetime.datetime.fromtimestamp(note.pdate/1000).year) if note.pdate else name.split()[-1]
                    pdf_url = f"https://openreview.net{note_content.get('pdf',{}).get('value')}" if note_content.get('pdf') else None

                    new_paper = Paper(
                        source='openreview', source_id=or_id, title=title,
                        authors=[{'name': author} for author in authors_list],
                        abstract=note_content.get('abstract', {}).get('value'),
                        paper_url=f"https://openreview.net/forum?id={or_id}", pdf_url=pdf_url,
                        venue_or_category=venue_id, year_or_date=str(year) if year else None,
                        keywords=keywords, category=category,
                        replies_data=replies_data if replies_data else None,
                        reputation_score=0.0
                    )
                    papers_to_commit.append(new_paper)
                
                if papers_to_commit:
                    session.add_all(papers_to_commit); session.commit()
                    print(f"  -> ✅ Success! Added {len(papers_to_commit)} new paper from {name}.")
                else:
                    print(f"  -> 🟡 No new papers to add for '{name}'.")

            except Exception as e:
                print(f"  -> ❌ ERROR processing venue '{name}': {e}")
                if session.in_transaction(): session.rollback()

    print("\n✅ All venue fetches complete.")

if __name__ == "__main__":
    fetch_papers_from_venues()