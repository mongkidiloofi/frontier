// The raw API response for a tag
export interface TagDTO {
  name: string;
  isRemovable: boolean;
}

// The clean, internal model for a Paper
export interface Paper {
  id: number;
  source: 'arxiv' | 'openreview';
  source_id: string;
  title: string;
  authors: string[];
  abstract: string | null;
  paper_url: string;
  pdf_url: string | null;
  venue_or_category: string;
  year_or_date: Date | null; // <-- Now a Date object
  tags: TagDTO[];
  upvotes: number;
  downvotes: number;
  category: string | null;
  bleeding_edge_score: number | null;
  recency_component: number | null;
  reputation_component: number | null;
  popularity_component: number | null;
}

// The raw API response for a Paper
export interface PaperDTO extends Omit<Paper, 'year_or_date'> {
  year_or_date: string | null; // <-- The raw string from the API
}

// The clean, internal model for a Comment
export interface Comment {
  id: number;
  body: string;
  created_at: Date; // <-- Now a Date object
  author_name: string;
}

// The raw API response for a Comment
export interface CommentReadDTO extends Omit<Comment, 'created_at'> {
  created_at: string; // <-- The raw string from the API
}