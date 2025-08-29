<script lang="ts">
  import { papers } from '$lib/stores/papers';
  import PaperItem from '$lib/components/PaperItem.svelte';
  import ControlBar from '$lib/components/ControlBar.svelte';
  import { intersect } from '$lib/actions/intersect';
  import { fly } from 'svelte/transition';

  // The store handles when to load more. The component just sends the signal.
  function loadNextPage() {
    papers.loadMore();
  }
</script>

<ControlBar />

<div class="feed">
  {#each $papers.papers as paper (paper.id)}
    <div in:fly={{ y: 20, duration: 300 }}>
      <PaperItem {paper} />
    </div>
  {/each}
</div>

<footer>
  <div class="sentinel" use:intersect={loadNextPage}></div>

  {#if $papers.loading}
    <p class="status">Loading...</p>
  {/if}

  {#if $papers.error}
    <p class="status error">{$papers.error}</p>
  {/if}

  {#if !$papers.hasMore && !$papers.loading && $papers.papers.length > 0}
    <p class="status">End of results.</p>
  {/if}
</footer>

<style>
  footer {
    text-align: center;
    padding: var(--space-8) 0;
    min-height: 50px;
  }
  
  .status {
    color: var(--color-text-tertiary);
  }

  .error {
    color: var(--color-error);
  }

  .sentinel {
    height: 10px;
  }
</style>