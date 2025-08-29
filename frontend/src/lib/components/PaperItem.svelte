<script lang="ts">
  import type { Paper } from '$lib/types';
  import PaperMetadata from './PaperMetadata.svelte';

  // --- THIS IS THE FIX ---
  // A component's props must be declared with `export let`.
  export let paper: Paper;
</script>

<article>
  <div class="content">
    <h2>
      <a href="/#/paper/{paper.id}">
        {paper.title}
      </a>
    </h2>
    <p class="authors">{paper.authors.join(', ')}</p>
  </div>
  <PaperMetadata {paper} />
</article>

<style>
  article {
    display: flex;
    flex-direction: column;
    gap: var(--space-4);
    padding-bottom: var(--space-8);
    margin-bottom: var(--space-8);
    border-bottom: 1px solid var(--color-border-subtle);
  }
  article:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
  h2 {
    font-size: var(--font-size-lg);
    font-weight: 600;
    line-height: 1.4;
    margin-bottom: var(--space-1);
  }
  h2 a {
    color: inherit;
    text-decoration: none;
  }
  h2 a:hover {
    color: var(--color-accent);
  }
  .authors {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    line-height: 1.5;
    margin: 0;
  }
</style>