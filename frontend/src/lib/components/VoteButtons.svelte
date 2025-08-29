<script lang="ts">
  import { papers } from '$lib/stores/papers';

  // --- THIS IS THE FIX ---
  // Declare the props being passed in from the parent component.
  export let paperId: number;
  export let upvotes: number;
  export let downvotes: number;
</script>

<div class="vote-buttons">
  <button class="vote-button" on:click={() => papers.vote(paperId, 'up')} title="Underrated">
    <svg width="16" height="16" viewBox="0 0 24 24"><path d="M12 5l0 14" /><path d="M18 11l-6 -6" /><path d="M6 11l6 -6" /></svg>
    <span>{upvotes}</span>
  </button>

  <button class="vote-button" on:click={() => papers.vote(paperId, 'down')} title="Overrated">
    <svg width="16" height="16" viewBox="0 0 24 24"><path d="M12 19l0 -14" /><path d="M18 13l-6 6" /><path d="M6 13l6 6" /></svg>
    <span>{downvotes}</span>
  </button>
</div>

<style>
  .vote-buttons { display: flex; gap: var(--space-3); align-items: center; }
  .vote-button {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    background: none;
    border: 1px solid transparent;
    border-radius: var(--border-radius-sm);
    padding: var(--space-1) var(--space-2);
    cursor: pointer;
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    transition: var(--transition-fast);
  }
  .vote-button:hover {
    background-color: var(--color-surface);
    border-color: var(--color-border);
  }
  .vote-button svg {
    stroke-width: 2.5;
    stroke: currentColor;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
</style>