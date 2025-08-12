import asyncio
import arxiv
from sqlalchemy import select, and_
from datetime import datetime

# Import the components from our application structure
from model.database import SessionMaker  # Assuming this path is correct
from model.paper import Paper # <-- CHANGED: Using the unified Paper model
from services.semantic_scholar_service import semantic_scholar_service # Assuming this path is correct

async def fetch_and_store_arxiv():
    """
    Fetches the latest papers from arXiv, calculates a reputation score,
    and stores them in the database using the unified Paper model.
    """
    client = arxiv.Client()
    
    # --- FINAL CATEGORY LIST ---
    categories = [
        "cs.AI",  # Artificial Intelligence
        "cs.CL",  # Computation and Language
        "cs.CV",  # Computer Vision
        "cs.LG",  # Machine Learning
        "cs.MA",  # Multiagent Systems
        "cs.RO",  # Robotics
    ]
    query_string = " OR ".join([f"cat:{cat}" for cat in categories])
    # --- END OF LIST ---

    search = arxiv.Search(
        query=query_string,
        max_results=100,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    print(f"Fetching latest {search.max_results} papers from specified categories...")
    results = client.results(search)

    # Use a single database session for the entire operation
    async with SessionMaker() as session:
        papers_to_add = []
        for result in results:
            arxiv_id = result.entry_id.split('/')[-1]

            # --- CHANGED: Check if this paper already exists using the unified model ---
            # We check for the source_id AND the source to be sure.
            existing_paper_query = select(Paper).where(
                and_(Paper.source_id == arxiv_id, Paper.source == 'arxiv')
            )
            existing_paper_result = await session.execute(existing_paper_query)
            if existing_paper_result.scalars().first():
                continue
            # --- END OF CHANGE ---

            print(f"\n-> Processing new paper: {result.title[:60]}...")
            
            # Prepare the author list
            authors_list = [{'name': author.name} for author in result.authors]

            # --- REPUTATION SCORING (No change here) ---
            print("   Querying Semantic Scholar for author reputation...")
            reputation_score = await semantic_scholar_service.calculate_paper_score(authors_list)
            print(f"  -> Calculated Total Reputation Score: {reputation_score}")
            # --- END OF SCORING ---

            # --- CHANGED: Create a new unified Paper object ---
            new_paper = Paper(
                source='arxiv',
                source_id=arxiv_id,
                title=result.title,
                authors=authors_list,
                abstract=result.summary.replace('\n', ' '),
                paper_url=result.entry_id,  # Link to the abstract page
                pdf_url=result.pdf_url,
                venue_or_category=result.primary_category, # Use primary category as the "venue"
                year_or_date=result.published.strftime("%Y-%m-%d"),
                keywords=result.categories, # Use all categories as keywords
                reputation_score=reputation_score,
                # These fields are not applicable to arXiv, so they are None by default
                category=None,
                replies_data=None
            )
            # --- END OF CHANGE ---
            
            papers_to_add.append(new_paper)
        
        if papers_to_add:
            print(f"\nAdding {len(papers_to_add)} new papers to the database...")
            session.add_all(papers_to_add)
            await session.commit()
            print("✅ Database commit successful.")
        else:
            print("\nNo new papers found to add.")
    
    print("✅ Fetcher run complete.")

if __name__ == "__main__":
    asyncio.run(fetch_and_store_arxiv())