import type { Paper, PaperDTO, Comment, CommentReadDTO } from '$lib/types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ message: 'An unknown error occurred' }));
    throw new Error(errorBody.detail || `API request failed: ${response.statusText}`);
  }
  if (response.status === 204) {
      return null as T;
  }
  return await response.json();
}

function transformPaper(dto: PaperDTO): Paper {
  return {
    ...dto,
    year_or_date: dto.year_or_date ? new Date(dto.year_or_date) : null,
  };
}

function transformComment(dto: CommentReadDTO): Comment {
  return {
    ...dto,
    created_at: new Date(dto.created_at),
  };
}

// --- THIS IS THE FIX ---
// The type name was corrected from `FetchPapers-Params` to `FetchPapersParams`.
export interface FetchPapersParams {
  source: 'arxiv' | 'openreview';
  limit?: number;
  offset?: number;
  tags?: string[];
  venue?: string;
  year?: number;
  category?: string;
}

export async function fetchPapers({
  source, limit = 20, offset = 0, tags = [], venue, year, category
}: FetchPapersParams): Promise<Paper[]> {
  const params = new URLSearchParams();
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  if (tags.length > 0) params.set('tags', tags.join(','));
  if (venue) params.set('venue', venue);
  if (year) params.set('year', String(year));
  if (category) params.set('category', category);

  const rawPapers = await apiFetch<PaperDTO[]>(`/api/papers/${source}?${params.toString()}`);
  return rawPapers.map(transformPaper);
}

export async function fetchPaperById(id: number): Promise<Paper> {
  const rawPaper = await apiFetch<PaperDTO>(`/api/papers/${id}`);
  return transformPaper(rawPaper);
}

export async function fetchAllTags(): Promise<string[]> {
  return apiFetch<string[]>('/api/tags/all');
}

export async function voteOnPaper(paperId: number, direction: 'up' | 'down'): Promise<void> {
  await apiFetch<void>(`/api/papers/${paperId}/vote`, {
    method: 'POST',
    body: JSON.stringify({ direction }),
  });
}

export async function fetchComments(paperId: number): Promise<Comment[]> {
  const rawComments = await apiFetch<CommentReadDTO[]>(`/api/papers/${paperId}/comments`);
  return rawComments.map(transformComment);
}

export async function postComment(paperId: number, body: string): Promise<Comment> {
  const rawComment = await apiFetch<CommentReadDTO>(`/api/papers/${paperId}/comments`, {
    method: 'POST',
    body: JSON.stringify({ body }),
  });
  return transformComment(rawComment);
}