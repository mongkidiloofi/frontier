import { writable } from 'svelte/store';
import { fetchComments, postComment } from '$lib/api';
import type { Comment } from '$lib/types';

interface CommentsStore {
  comments: Comment[];
  loading: boolean;
  error: string | null;
}

function createCommentsStore() {
  const { subscribe, set, update } = writable<CommentsStore>({
    comments: [],
    loading: true,
    error: null,
  });

  async function load(paperId: number) {
    set({ comments: [], loading: true, error: null });
    try {
      const comments = await fetchComments(paperId);
      set({ comments, loading: false, error: null });
    } catch (e: any) {
      set({ comments: [], loading: false, error: 'Could not load comments.' });
    }
  }

  async function add(paperId: number, body: string) {
    // Optimistic update
    const tempId = -Math.random();
    const newComment: Comment = {
      id: tempId,
      body,
      created_at: new Date(),
      author_name: 'Anonymous',
    };
    update(s => ({ ...s, comments: [newComment, ...s.comments], error: null }));

    try {
      const savedComment = await postComment(paperId, body);
      // Replace the temporary comment with the real one
      update(s => ({
        ...s,
        comments: s.comments.map(c => c.id === tempId ? savedComment : c)
      }));
    } catch (e: any) {
      // Rollback on failure and set an error message
      update(s => ({
        ...s,
        comments: s.comments.filter(c => c.id !== tempId),
        error: "Failed to post comment. Please try again."
      }));
    }
  }

  return { subscribe, load, add };
}

export const comments = createCommentsStore();