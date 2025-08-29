import { writable } from 'svelte/store';
import { fetchAllTags } from '$lib/api';

interface AllTagsStore {
  tags: string[];
  loading: boolean;
  error: string | null;
}

function createAllTagsStore() {
  const { subscribe, set } = writable<AllTagsStore>({
    tags: [],
    loading: true,
    error: null,
  });

  async function load() {
    try {
      const allTags = await fetchAllTags();
      set({ tags: allTags, loading: false, error: null });
    } catch (e: any) {
      set({ tags: [], loading: false, error: 'Could not load tags.' });
      console.error(e);
    }
  }

  // The store is autonomous. It loads its own data.
  load();

  return {
    subscribe,
  };
}

export const allTags = createAllTagsStore();