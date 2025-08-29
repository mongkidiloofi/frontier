<script lang="ts">
  import type { Paper } from '$lib/types';
  import VoteButtons from './VoteButtons.svelte';
  import ScoreDisplay from './ScoreDisplay.svelte';

  export let paper: Paper;

  $: allTags = [...new Set([
    ...(paper.category ? [paper.category] : []),
    ...paper.tags.map(tag => tag.name)
  ])];

  const formatDate = (date: Date | null) => {
    if (!date) return '';
    return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  }
</script>

<footer class="article-footer">
  <div class="metadata-group">
    {#if paper.source === 'arxiv'}
      <div class="actions">
        <VoteButtons paperId={paper.id} upvotes={paper.upvotes} downvotes={paper.downvotes} />
      </div>
      <span class="separator">&middot;</span>
    {/if}

    <span class="date">
      {#if paper.source === 'openreview'}
        {paper.venue_or_category}
      {:else}
        {formatDate(paper.year_or_date)}
      {/if}
    </span>
    
    {#if allTags.length > 0}
      <span class="separator">&middot;</span>
      <div class="tags">
        {#each allTags as tag (tag)}
          <span class="tag-pill">{tag}</span>
        {/each}
      </div>
    {/if}
  </div>
  
  <div class="scores">
    {#if paper.source === 'arxiv'}
      <ScoreDisplay
        finalScore={paper.bleeding_edge_score}
        recency={paper.recency_component}
        reputation={paper.reputation_component}
        popularity={paper.popularity_component}
      />
    {/if}
  </div>
</footer>

<style>
  .article-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--space-6);
    min-height: 28px;
    font-size: var(--font-size-sm);
  }
  .metadata-group {
    display: flex;
    align-items: center;
    gap: var(--space-3);
    flex-wrap: wrap;
    flex-grow: 1;
  }
  .scores { flex-shrink: 0; }
  .date { color: var(--color-text-secondary); white-space: nowrap; }
  .separator { color: var(--color-border); }
  .tags { display: flex; flex-wrap: wrap; gap: var(--space-2); }
  .tag-pill {
    font-size: var(--font-size-xs);
    background-color: var(--color-surface);
    color: var(--color-text-secondary);
    padding: var(--space-1) var(--space-2);
    border-radius: var(--border-radius-sm);
    font-weight: 500;
  }
</style>