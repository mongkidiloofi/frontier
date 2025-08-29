<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  let body = '';
  const dispatch = createEventDispatcher();

  function handleSubmit() {
    if (!body.trim()) return;
    dispatch('submit', { body });
    body = '';
  }
</script>

<form class="comment-form" on:submit|preventDefault={handleSubmit}>
  <textarea placeholder="Add a comment..." bind:value={body}></textarea>
  <button type="submit" disabled={!body.trim()}>Post</button>
</form>

<style>
  .comment-form { display: flex; flex-direction: column; gap: var(--space-3); }
  textarea {
    font-family: var(--font-sans);
    font-size: var(--font-size-base);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
    padding: var(--space-3);
    min-height: 80px;
    resize: vertical;
    transition: var(--transition-fast);
  }
  textarea:focus {
    outline: none;
    border-color: var(--color-accent);
  }
  button {
    align-self: flex-end;
    background-color: var(--color-text-primary);
    color: var(--color-background);
    border: none;
    border-radius: var(--border-radius-md);
    padding: var(--space-2) var(--space-4);
    font-weight: 500;
    cursor: pointer;
    transition: var(--transition-fast);
  }
  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
</style>