<script lang="ts">
  import type { Comment } from '$lib/types';
  export let comment: Comment;

  // A simple relative time formatter
  function formatRelativeTime(date: Date): string {
    const now = new Date();
    const seconds = Math.round((now.getTime() - date.getTime()) / 1000);
    const minutes = Math.round(seconds / 60);
    const hours = Math.round(minutes / 60);
    const days = Math.round(hours / 24);

    if (seconds < 60) return "just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
</script>

<div class="comment">
  <p class="meta">{comment.author_name} &middot; {formatRelativeTime(comment.created_at)}</p>
  <p class="body">{comment.body}</p>
</div>

<style>
  .comment {
    padding: var(--space-4) 0;
    border-bottom: 1px solid var(--color-border-subtle);
  }
  .comment:last-child {
    border-bottom: none;
  }
  .meta {
    font-size: var(--font-size-sm);
    color: var(--color-text-tertiary);
    margin: 0 0 var(--space-2) 0;
  }
  .body {
    font-size: var(--font-size-base);
    line-height: 1.6;
    margin: 0;
    white-space: pre-wrap;
    color: var(--color-text-secondary);
  }
</style>