<script>
  import { onMount } from 'svelte';
  // Import the reusable component. The path assumes it's in src/lib/components/
  import PaperCard from './lib/components/PaperCard.svelte';

  // --- STATE VARIABLES ---
  let arxivPapers = [];
  let openReviewPapers = [];
  
  let isLoadingArxiv = true;
  let isLoadingOpenReview = true;
  let error = null; // A single error state for simplicity

  // This variable controls which tab is currently visible
  let activeTab = 'arxiv'; // Can be 'arxiv' or 'openreview'

  // --- DATA FETCHING ---
  onMount(() => {
    // We run two independent fetch operations. This is more robust than Promise.all
    // and allows one feed to load even if the other fails.

    // Fetch arXiv papers (the reputation-ranked feed)
    fetch('http://127.0.0.1:8000/api/papers/arxiv')
      .then(response => {
        if (!response.ok) throw new Error(`arXiv fetch failed: ${response.status}`);
        return response.json();
      })
      .then(data => {
        arxivPapers = data;
      })
      .catch(e => {
        console.error("arXiv fetch error:", e);
        error = error ? `${error}\n${e.message}` : e.message;
      })
      .finally(() => {
        isLoadingArxiv = false;
      });

    // Fetch OpenReview papers (the peer-reviewed feed)
    fetch('http://127.0.0.1:8000/api/papers/openreview')
      .then(response => {
        if (!response.ok) throw new Error(`OpenReview fetch failed: ${response.status}`);
        return response.json();
      })
      .then(data => {
        openReviewPapers = data;
      })
      .catch(e => {
        console.error("OpenReview fetch error:", e);
        error = error ? `${error}\n${e.message}` : e.message;
      })
      .finally(() => {
        isLoadingOpenReview = false;
      });
  });
</script>

<!-- The <main> tag is now the top-level element in this component -->
<main class="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
    
  <header class="text-center pb-6 mb-8 border-b border-slate-200">
    <h1 class="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">Frontier</h1>
    <p class="mt-2 text-lg text-slate-600">The bleeding edge of AI research, curated and ranked.</p>
  </header>

  <!-- Tab Navigation -->
  <div class="mb-8 flex justify-center border-b border-slate-200">
    <button 
      class="px-6 py-3 font-semibold transition-colors duration-200 focus:outline-none"
      class:text-blue-600={activeTab === 'arxiv'}
      class:border-b-2={activeTab === 'arxiv'}
      class:border-blue-600={activeTab === 'arxiv'}
      class:text-slate-500={activeTab !== 'arxiv'}
      on:click={() => activeTab = 'arxiv'}>
      Latest Pre-prints
    </button>
    <button 
      class="px-6 py-3 font-semibold transition-colors duration-200 focus:outline-none"
      class:text-blue-600={activeTab === 'openreview'}
      class:border-b-2={activeTab === 'openreview'}
      class:border-blue-600={activeTab === 'openreview'}
      class:text-slate-500={activeTab !== 'openreview'}
      on:click={() => activeTab = 'openreview'}>
      Top Conference Papers
    </button>
  </div>

  <!-- Main Content Area -->
  <div>
    {#if error && !isLoadingArxiv && !isLoadingOpenReview}
      <div class="bg-red-100 border border-red-300 text-red-800 rounded-lg p-6 text-center">
        <p class="font-bold">Could Not Fetch Papers</p>
        <p class="mt-2">Error: {error}</p>
      </div>
    {/if}

    {#if activeTab === 'arxiv'}
      {#if isLoadingArxiv}
        <p class="text-center text-slate-500 py-8">Loading arXiv papers...</p>
      {:else if arxivPapers.length === 0 && !error}
        <p class="text-center text-slate-500 py-8">No new arXiv papers found.</p>
      {:else}
        <div class="space-y-8">
          {#each arxivPapers as paper (paper.id)}
            <PaperCard {paper} />
          {/each}
        </div>
      {/if}
    {:else if activeTab === 'openreview'}
      {#if isLoadingOpenReview}
        <p class="text-center text-slate-500 py-8">Loading OpenReview papers...</p>
      {:else if openReviewPapers.length === 0 && !error}
        <p class="text-center text-slate-500 py-8">No new OpenReview papers found.</p>
      {:else}
        <div class="space-y-8">
          {#each openReviewPapers as paper (paper.id)}
            <PaperCard {paper} />
          {/each}
        </div>
      {/if}
    {/if}
  </div>

</main>

<!-- No <style> block is needed here as Tailwind handles all styling via classes -->