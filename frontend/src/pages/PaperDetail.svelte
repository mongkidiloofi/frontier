<script lang="ts">
  import { params } from 'svelte-spa-router';
  import { fetchPaperById } from '$lib/api';
  import type { Paper } from '$lib/types';
  import PaperMetadata from '$lib/components/PaperMetadata.svelte';
  import CommentThread from '$lib/components/CommentThread.svelte';

  let paper: Paper | null = null;
  let isLoading = true;
  let error: string | null = null;

  $: {
    const idFromParams = $params?.id; 
    if (idFromParams) {
      const parsedId = parseInt(idFromParams, 10);
      if (!isNaN(parsedId)) {
        loadPaper(parsedId);
      } else {
        error = 'Invalid paper ID in URL.';
        isLoading = false;
      }
    }
  }

  async function loadPaper(id: number) {
    isLoading = true;
    error = null;
    paper = null;
    try {
      paper = await fetchPaperById(id);
    } catch (e: any) {
      error = e.message || 'Failed to load paper.';
      console.error(e);
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="paper-detail">
  {#if isLoading}
    <div class="skeleton-loader">
      <div class="skeleton-line title"></div>
      <div class="skeleton-line authors"></div>
      <div class="skeleton-line links"></div>
      <hr class="divider" />
      <div class="skeleton-line abstract"></div>
      <div class="skeleton-line abstract short"></div>
      <div class="skeleton-line abstract medium"></div>
    </div>
  {:else if error}
    <p class="status error">{error}</p>
  {:else if paper}
    <article>
      <h1>{paper.title}</h1>
      <p class="authors">{paper.authors.join(', ')}</p>

      <div class="external-links">
        <a href={paper.paper_url} target="_blank" rel="noopener noreferrer">View on {paper.source === 'arxiv' ? 'arXiv' : 'OpenReview'}</a>
        {#if paper.pdf_url}
          <span class="separator">&middot;</span>
          <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">Download PDF</a>
        {/if}
      </div>

      <hr class="divider" />

      <p class="abstract">{paper.abstract}</p>

      <PaperMetadata {paper} />
      <CommentThread paperId={paper.id} />
    </article>
  {/if}
</div>

<style>
  .paper-detail { padding-bottom: var(--space-16); }
  .status { text-align: center; color: var(--color-text-tertiary); padding: var(--space-16) 0; }
  .error { color: var(--color-error); }
  h1 { font-size: var(--font-size-3xl); font-weight: 700; line-height: 1.3; margin-bottom: var(--space-4); }
  .authors { font-size: var(--font-size-lg); color: var(--color-text-secondary); margin-bottom: var(--space-6); }
  .external-links { font-size: var(--font-size-sm); }
  .external-links a:hover { text-decoration: underline; }
  .external-links .separator { color: #ccc; margin: 0 var(--space-2); }
  .divider { border: none; border-top: 1px solid var(--color-border); margin: var(--space-8) 0; }
  .abstract { font-size: var(--font-size-base); line-height: 1.7; color: var(--color-text-primary); white-space: pre-wrap; margin-bottom: var(--space-12); }
  
  /* Skeleton Loader Styles */
  @keyframes shimmer { 0% { background-position: -1000px 0; } 100% { background-position: 1000px 0; } }
  .skeleton-line {
    background-color: #f0f0f0;
    background-image: linear-gradient(to right, #f0f0f0 0%, #e0e0e0 20%, #f0f0f0 40%, #f0f0f0 100%);
    background-repeat: no-repeat;
    background-size: 2000px 104px;
    animation: shimmer 1.5s linear infinite;
    border-radius: var(--border-radius-sm);
  }
  .skeleton-line.title { height: 36px; max-width: 80%; margin-bottom: var(--space-4); }
  .skeleton-line.authors { height: 24px; max-width: 50%; margin-bottom: var(--space-6); }
  .skeleton-line.links { height: 20px; max-width: 30%; }
  .skeleton-line.abstract { height: 16px; margin-bottom: var(--space-3); max-width: 100%; }
  .skeleton-line.short { max-width: 60%; }
  .skeleton-line.medium { max-width: 90%; }
</style>