import asyncio
import arxiv
from sqlalchemy import select
from datetime import datetime

# Import the components from our application structure
from model.database import SessionMaker
from model.arxiv_paper import ArxivPaper
from services.semantic_scholar_service import semantic_scholar_service

async def fetch_and_store_arxiv():
    """
    Fetches the latest papers from arXiv for a broad set of CS categories,
    calculates a reputation score by querying the Semantic Scholar API,
    and stores new papers in the database.
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
        max_results=100,  # <-- Set back to 100
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    print(f"Fetching latest {search.max_results} papers from specified categories...")
    results = client.results(search)

    # Use a single database session for the entire operation
    async with SessionMaker() as session:
        papers_to_add = []
        for result in results:
            arxiv_id = result.entry_id.split('/')[-1]

            # Check if this paper already exists in our database
            existing_paper_query = select(ArxivPaper).where(ArxivPaper.arxiv_id == arxiv_id)
            existing_paper_result = await session.execute(existing_paper_query)
            if existing_paper_result.scalars().first():
                continue

            print(f"\n-> Processing new paper: {result.title[:60]}...")
            
            # Prepare the author list in the format our service expects
            authors_list = [{'name': author.name} for author in result.authors]

            # --- REPUTATION SCORING ---
            print("   Querying Semantic Scholar for author reputation...")
            reputation_score = await semantic_scholar_service.calculate_paper_score(authors_list)
            print(f"  -> Calculated Total Reputation Score: {reputation_score}")
            # --- END OF SCORING ---

            # Create a new ArxivPaper object with all the data
            new_paper = ArxivPaper(
                arxiv_id=arxiv_id,
                title=result.title,
                authors=authors_list,
                abstract=result.summary.replace('\n', ' '),
                pdf_url=result.pdf_url,
                submitted_date=result.published.strftime("%Y-%m-%d"),
                reputation_score=reputation_score
            )
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