from sqlalchemy import select, func, cast, Float, or_, case, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select
from typing import List
from dataclasses import dataclass
from datetime import date

from model.paper import Paper

@dataclass
class RankedPaper:
    paper: Paper
    bleeding_edge_score: float
    recency_component: float
    reputation_component: float
    popularity_component: float

WEIGHT_RECENCY = 0.3
WEIGHT_REPUTATION = 0.5
WEIGHT_POPULARITY = 0.2
RECENCY_DECAY_CONSTANT = 0.1

class RankingService:
    # --- THIS IS THE REFACTOR ---
    # The core ranking logic is now in a private method that accepts any pre-filtered query.
    async def _get_ranked_papers(
        self, session: AsyncSession, base_query: Select, limit: int, offset: int
    ) -> List[RankedPaper]:
        
        filtered_subquery = base_query.subquery('filtered_papers')

        # Recency Score Calculation
        days_old = case(
            (filtered_subquery.c.year_or_date > date.today(), 0),
            else_=func.extract('epoch', func.now() - filtered_subquery.c.year_or_date) / (60*60*24)
        )
        recency_score = func.exp(-RECENCY_DECAY_CONSTANT * days_old).label("recency_score")
        
        # Popularity Score Calculation (Wilson Score Interval)
        upvotes = filtered_subquery.c.upvotes
        downvotes = filtered_subquery.c.downvotes
        total_votes = (upvotes + downvotes)
        upvotes_float = cast(upvotes, Float)
        total_votes_float = cast(total_votes, Float)
        safe_total_votes = func.greatest(total_votes_float, 1.0)
        p_hat = upvotes_float / safe_total_votes
        z = 1.96 # 95% confidence
        sqrt_part = func.sqrt((p_hat * (1 - p_hat) + z * z / (4 * safe_total_votes)) / safe_total_votes)
        popularity_score = ((p_hat + z * z / (2 * safe_total_votes) - z * sqrt_part) / (1 + z * z / safe_total_votes)).label("popularity_score")
        
        # Reputation Score (Log-transformed)
        reputation = filtered_subquery.c.reputation_score
        log_reputation = func.log(reputation + 1).label("log_reputation")
        
        # Min-Max Normalization using Window Functions
        max_rep = func.max(log_reputation).over()
        min_rep = func.min(log_reputation).over()
        max_rec = func.max(recency_score).over()
        min_rec = func.min(recency_score).over()
        max_pop = func.max(popularity_score).over()
        min_pop = func.min(popularity_score).over()

        # Handle division by zero if all values in a window are the same
        norm_log_reputation = case((max_rep == min_rep, 1.0), else_=((log_reputation - min_rep) / (max_rep - min_rep + 1e-9))).label("norm_log_reputation")
        norm_recency = case((max_rec == min_rec, 1.0), else_=((recency_score - min_rec) / (max_rec - min_rec + 1e-9))).label("norm_recency")
        norm_popularity = case((max_pop == min_pop, 1.0), else_=((popularity_score - min_pop) / (max_pop - min_pop + 1e-9))).label("norm_popularity")

        # Final Weighted Score
        bleeding_edge_score = (
            (WEIGHT_RECENCY * norm_recency) + 
            (WEIGHT_REPUTATION * norm_log_reputation) + 
            (WEIGHT_POPULARITY * norm_popularity)
        ).label("bleeding_edge_score")
        
        # The final query selects all original paper columns plus the calculated scores
        final_query = select(
            filtered_subquery,
            bleeding_edge_score,
            norm_recency,
            norm_log_reputation,
            norm_popularity
        ).order_by(bleeding_edge_score.desc()).offset(offset).limit(limit)
        
        result = await session.execute(final_query)
        
        # Manually construct the Paper objects from the flat row data to avoid ORM issues with complex queries
        ranked_papers = []
        for row in result.all():
            paper_data = {c.name: getattr(row, c.name) for c in filtered_subquery.c}
            
            ranked_papers.append(
                RankedPaper(
                    paper=Paper(**paper_data),
                    bleeding_edge_score=row.bleeding_edge_score,
                    recency_component=row.norm_recency,
                    reputation_component=row.norm_log_reputation,
                    popularity_component=row.norm_popularity
                )
            )
        return ranked_papers

    # Public method for arXiv papers
    async def get_ranked_arxiv_papers(
        self, session: AsyncSession, limit: int = 50, offset: int = 0, tags: List[str] | None = None
    ) -> List[RankedPaper]:
        
        base_query = select(Paper).where(Paper.source == 'arxiv')
        if tags:
            base_query = base_query.where(
                or_(Paper.keywords.contains(tags), Paper.user_tags.contains(tags))
            )
        
        return await self._get_ranked_papers(session, base_query, limit, offset)

    # --- NEW: Public method for OpenReview papers ---
    async def get_ranked_openreview_papers(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        tags: List[str] | None = None,
        venue: str | None = None,
        year: int | None = None,
        category: str | None = None,
    ) -> List[RankedPaper]:
        
        base_query = select(Paper).where(Paper.source == 'openreview')

        if tags:
            # Note: OpenReview filtering doesn't use user_tags yet, just keywords
            base_query = base_query.where(Paper.keywords.contains(tags))
        if venue:
            base_query = base_query.where(Paper.venue_or_category.ilike(f"%{venue}%"))
        if year:
            base_query = base_query.where(func.extract('year', Paper.year_or_date) == year)
        if category:
            base_query = base_query.where(Paper.category == category)
        
        # Since OpenReview papers have no votes, their popularity and reputation are 0.
        # We order by date to ensure a stable, sensible default ranking.
        base_query = base_query.order_by(Paper.year_or_date.desc(), Paper.id.desc())
        
        return await self._get_ranked_papers(session, base_query, limit, offset)

ranking_service = RankingService()