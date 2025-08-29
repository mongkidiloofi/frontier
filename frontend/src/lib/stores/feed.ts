import { writable } from 'svelte/store';

export type Source = 'arxiv' | 'openreview';

interface ArxivFilters {
  tags: string[];
}

interface OpenReviewFilters {
  tags: string[];
  venue: string | null;
  year: number | null;
  category: string | null;
}

interface FeedState {
  activeSource: Source;
  filters: {
    arxiv: ArxivFilters;
    openreview: OpenReviewFilters;
  };
}

const initialState: FeedState = {
  activeSource: 'arxiv',
  filters: {
    arxiv: {
      tags: [],
    },
    openreview: {
      tags: [],
      venue: null,
      year: null,
      category: null,
    },
  },
};

function createFeedStore() {
  const { subscribe, set, update } = writable<FeedState>(initialState);

  const getActiveFilters = (state: FeedState) => state.filters[state.activeSource];

  return {
    subscribe,
    setSource: (source: Source) => update(s => ({ ...s, activeSource: source })),
    
    addTag: (tag: string) => update(s => {
      const activeFilters = getActiveFilters(s);
      if (tag && !activeFilters.tags.includes(tag)) {
        activeFilters.tags = [...activeFilters.tags, tag];
      }
      return s;
    }),

    removeTag: (tagToRemove: string) => update(s => {
      const activeFilters = getActiveFilters(s);
      activeFilters.tags = activeFilters.tags.filter(t => t !== tagToRemove);
      return s;
    }),

    // OpenReview-specific setters
    setVenue: (venue: string | null) => update(s => {
      s.filters.openreview.venue = venue;
      return s;
    }),
    setYear: (year: number | null) => update(s => {
      s.filters.openreview.year = year;
      return s;
    }),
    setCategory: (category: string | null) => update(s => {
      s.filters.openreview.category = category;
      return s;
    }),
  };
}

export const feed = createFeedStore();