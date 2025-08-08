# in frontier/services/arxiv_fetcher.py
import asyncio
import arxiv
from sqlalchemy import select
from model.database import SessionMaker
from model.arxiv_paper import ArxivPaper

async def fetch_and_store_arxiv():
    client = arxiv.Client()
    
    search = arxiv.Search(
        query="cat:cs.LG",
        max_results=100,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    print("Fetching latest 100 papers from cs.LG...")
    results = client.results(search)

    async with SessionMaker() as session:
        papers_to_add = []
        for result in results:
            arxiv_id = result.entry_id.split('/')[-1]

            # --- THIS IS THE CORRECTED SECTION ---
            # We use a standard 'select' statement to check for existence
            # based on the unique 'arxiv_id' column.
            existing_paper_query = select(ArxivPaper).where(ArxivPaper.arxiv_id == arxiv_id)
            result_proxy = await session.execute(existing_paper_query)
            
            # .scalars().first() will be the ArxivPaper object if found, or None if not.
            if result_proxy.scalars().first():
                continue
            # --- END OF CORRECTION ---

            print(f"  -> Adding: {result.title[:60]}...")
            
            new_paper = ArxivPaper(
                arxiv_id=arxiv_id,
                title=result.title,
                authors=[{'name': author.name} for author in result.authors],
                abstract=result.summary.replace('\n', ' '),
                pdf_url=result.pdf_url,
                submitted_date=result.published.strftime("%Y-%m-%d")
            )
            papers_to_add.append(new_paper)
        
        if papers_to_add:
            session.add_all(papers_to_add)
            await session.commit()
    
    print(f"✅ Done. Added {len(papers_to_add)} new papers to the database.")

if __name__ == "__main__":
    asyncio.run(fetch_and_store_arxiv())