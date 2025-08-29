import { writable, derived, get } from 'svelte/store';
// --- THIS IS THE FIX ---
// The imported type name was corrected.
import { fetchPapers, voteOnPaper, type FetchPapersParams } from '$lib/api';
import type { Paper } from '$lib/types';
import { feed } from '$lib/stores/feed';

interface PapersStore {
  papers: Paper[];
  loading: boolean;
  hasMore: boolean;
  error: string | null;
}

function createPapersStore() {
  const store = writable<PapersStore>({
    papers: [],
    loading: false,
    hasMore: true,
    error: null,
  });
  const { subscribe, set, update } = store;

  let offset = 0;
  const limit = 20;

  const currentFilters = derived(feed, $feed => {
    if ($feed.activeSource === 'arxiv') {
      return {
        source: 'arxiv' as const,
        ...$feed.filters.arxiv
      };
    } else {
      return {
        source: 'openreview' as const,
        ...$feed.filters.openreview
      };
    }
  });

  currentFilters.subscribe(filters => {
    if (!filters) return;
    reset();
    loadMore();
  });

  async function loadMore() {
    const papersState = get(store);
    if (papersState.loading || !papersState.hasMore) return;
    
    const currentFilterState = get(currentFilters);

    update(s => ({ ...s, loading: true, error: null }));

    try {
      // --- THIS IS THE FIX ---
      // The type annotation was corrected.
      let apiParams: FetchPapersParams;

      if (currentFilterState.source === 'arxiv') {
        apiParams = {
          source: currentFilterState.source,
          tags: currentFilterState.tags,
          limit,
          offset,
        };
      } else {
        apiParams = {
          source: currentFilterState.source,
          tags: currentFilterState.tags,
          venue: currentFilterState.venue,
          year: currentFilterState.year,
          category: currentFilterState.category,
          limit,
          offset,
        };
      }
      
      const newPapers = await fetchPapers(apiParams);

      update(s => ({
        papers: [...s.papers, ...newPapers],
        loading: false,
        hasMore: newPapers.length === limit,
        error: null,
      }));

      offset += newPapers.length;
    } catch (error: any) {
      console.error("Failed to load more papers:", error);
      update(s => ({ ...s, loading: false, error: error.message || "Failed to load papers." }));
    }
  }
  
  function reset() {
    offset = 0;
    set({ papers: [], loading: false, hasMore: true, error: null });
  }

  async function vote(paperId: number, direction: 'up' | 'down') {
    let originalPaper: Paper | undefined;

    update(s => {
      const paperIndex = s.papers.findIndex(p => p.id === paperId);
      if (paperIndex === -1) return s;

      originalPaper = s.papers[paperIndex];

      const updatedPaper = { ...originalPaper };
      if (direction === 'up') updatedPaper.upvotes++;
      else updatedPaper.downvotes++;
      
      const newPapers = [...s.papers];
      newPapers[paperIndex] = updatedPaper;
      
      return { ...s, papers: newPapers };
    });

    try {
      await voteOnPaper(paperId, direction);
    } catch (error) {
      console.error("Vote failed:", error);
      if (originalPaper) {
        update(s => {
            const paperIndex = s.papers.findIndex(p => p.id === paperId);
            if (paperIndex === -1) return s;

            const newPapers = [...s.papers];
            newPapers[paperIndex] = originalPaper!;

            return { ...s, papers: newPapers, error: "Your vote could not be saved." };
        });
      }
    }
  }

  return {
    subscribe,
    loadMore,
    vote,
  };
}

export const papers = createPapersStore();