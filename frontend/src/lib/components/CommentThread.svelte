<script lang="ts">
  import { comments } from '$lib/stores/comments';
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import CommentItem from './CommentItem.svelte';
  import CommentForm from './CommentForm.svelte';

  export let paperId: number;

  onMount(() => {
    comments.load(paperId);
  });

  function handleCommentSubmit(event: CustomEvent<{ body: string }>) {
    comments.add(paperId, event.detail.body);
  }
</script>

<section class="comment-thread">
  <h3>Discussion</h3>
  <CommentForm on:submit={handleCommentSubmit} />
  
  {#if $comments.error}
    <p class="status error">{$comments.error}</p>
  {/if}

  <div class="comment-list">
    {#if $comments.loading}
      <p class="status">Loading comments...</p>
    {:else if $comments.comments.length === 0}
      <p class="status">No comments yet.</p>
    {:else}
      {#each $comments.comments as comment (comment.id)}
        <div in:fly={{ y: 20, duration: 300 }}>
          <CommentItem {comment} />
        </div>
      {/each}
    {/if}
  </div>
</section>

<style>
  .comment-thread { margin-top: var(--space-12); }
  h3 {
    font-size: var(--font-size-xl);
    margin-bottom: var(--space-6);
    border-bottom: 1px solid var(--color-border);
    padding-bottom: var(--space-3);
  }
  .comment-list { margin-top: var(--space-8); }
  .status {
    text-align: center;
    color: var(--color-text-tertiary);
    padding: var(--space-8) 0;
  }
  .error {
    color: var(--color-error);
    background-color: #fff0f0;
    border: 1px solid #ffd6d6;
    border-radius: var(--border-radius-md);
    padding: var(--space-3) var(--space-4);
    margin-top: var(--space-4);
    text-align: left;
  }
</style>