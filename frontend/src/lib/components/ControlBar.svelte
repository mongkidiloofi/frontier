<script lang="ts">
  import { feed, type Source } from '$lib/stores/feed';
  import { allTags } from '$lib/stores/tags';
  import { fly } from 'svelte/transition';

  let tagInputValue = '';

  const years = [2025, 2024, 2023];
  const venues = ['NeurIPS', 'ICLR', 'ICML', 'AISTATS', 'CoRL', 'TMLR', 'DMLR'];
  const categories = ['Oral', 'Spotlight', 'Poster'];

  function handleTagSubmit() {
    if (!tagInputValue.trim()) return;
    feed.addTag(tagInputValue);
    tagInputValue = '';
  }

  // Reactive variables for cleaner access
  $: activeSource = $feed.activeSource;
  // This is safe for properties that exist on BOTH filter types, like `tags`
  $: activeFilters = $feed.filters[activeSource];
</script>

<div class="control-bar">
  <div class="source-selector">
    <button class:active={activeSource === 'arxiv'} on:click={() => feed.setSource('arxiv')}>
      arXiv
    </button>
    <button class:active={activeSource === 'openreview'} on:click={() => feed.setSource('openreview')}>
      OpenReview
    </button>
  </div>

  <div class="filter-section">
    {#key activeSource}
      <div class="filters-wrapper" in:fly={{ y: -10, duration: 200 }} out:fly={{ y: -10, duration: 200 }}>
        {#if activeSource === 'arxiv'}
          <input
            type="text"
            list="all-tags-list"
            placeholder={$allTags.loading ? 'Loading tags...' : 'Filter by tags...'}
            disabled={$allTags.loading}
            bind:value={tagInputValue}
            on:keydown={(e) => e.key === 'Enter' && handleTagSubmit()}
          />
          <datalist id="all-tags-list">
            {#each $allTags.tags as tag (tag)}
              <option value={tag}></option>
            {/each}
          </datalist>
        {:else if activeSource === 'openreview'}
          <!-- --- THIS IS THE FIX --- -->
          <!-- We directly access the specific, correctly-typed filter object from the store. -->
          <!-- This removes the type ambiguity that the language server was complaining about. -->
          <select value={$feed.filters.openreview.venue} on:change={(e) => feed.setVenue(e.currentTarget.value || null)}>
            <option value="">All Venues</option>
            {#each venues as venue}
              <option value={venue}>{venue}</option>
            {/each}
          </select>
          <select value={$feed.filters.openreview.year} on:change={(e) => feed.setYear(e.currentTarget.value ? parseInt(e.currentTarget.value) : null)}>
            <option value="">All Years</option>
            {#each years as year}
              <option value={year}>{year}</option>
            {/each}
          </select>
          <select value={$feed.filters.openreview.category} on:change={(e) => feed.setCategory(e.currentTarget.value || null)}>
            <option value="">All Categories</option>
            {#each categories as category}
              <option value={category}>{category}</option>
            {/each}
          </select>
        {/if}
      </div>
    {/key}
  </div>
</div>

{#if activeFilters.tags.length > 0}
  <div class="active-tags">
    {#each activeFilters.tags as tag (tag)}
      <div class="tag-pill" in:fly={{ y: 5, duration: 200 }}>
        {tag}
        <button class="remove-tag" on:click={() => feed.removeTag(tag)}>
          &times;
        </button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .control-bar { display: flex; align-items: center; flex-wrap: wrap; gap: var(--space-6); margin-bottom: var(--space-6); }
  .source-selector { display: inline-flex; border: 1px solid var(--color-border); border-radius: var(--border-radius-full); padding: var(--space-1); }
  .source-selector button { background: none; border: none; border-radius: var(--border-radius-full); padding: var(--space-2) var(--space-4); cursor: pointer; font-size: var(--font-size-sm); font-weight: 500; color: var(--color-text-secondary); transition: var(--transition-fast); }
  .source-selector button.active { background-color: var(--color-text-primary); color: var(--color-background); }
  .source-selector button:not(.active):hover { background-color: var(--color-surface); }
  
  .filter-section { display: flex; }
  .filters-wrapper { display: flex; gap: var(--space-3); }

  .filter-section input, .filter-section select {
    font-family: var(--font-sans);
    font-size: var(--font-size-sm);
    padding: var(--space-2) var(--space-3);
    border: 1px solid var(--color-border);
    border-radius: var(--border-radius-md);
    min-width: 150px;
    background-color: var(--color-surface);
    transition: var(--transition-fast);
  }
  .filter-section input:focus, .filter-section select:focus {
    outline: none;
    border-color: var(--color-accent);
    background-color: var(--color-background);
  }

  .active-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-12); }
  .tag-pill { display: inline-flex; align-items: center; gap: var(--space-2); background-color: var(--color-surface); color: var(--color-text-secondary); padding: var(--space-1) var(--space-3); border-radius: var(--border-radius-full); font-size: var(--font-size-xs); font-weight: 500; }
  .remove-tag { background: none; border: none; padding: 0; margin: 0; cursor: pointer; font-size: 1.2em; line-height: 1; color: var(--color-text-tertiary); transition: var(--transition-fast); }
  .remove-tag:hover { color: var(--color-text-primary); }
</style>