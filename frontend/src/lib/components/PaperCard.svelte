<script>
  // 'export let' creates a "prop". This component expects to be given a 'paper' object.
  export let paper;
</script>

<article class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-lg hover:border-blue-400 transition-all duration-200 ease-in-out">
  
  <div class="flex justify-between items-center text-xs text-slate-500 mb-3">
    <!-- Conditionally show the Reputation Score only for arXiv papers -->
    {#if paper.source === 'arxiv'}
      <span class="font-semibold bg-blue-100 text-blue-800 rounded-full px-3 py-1">
        Reputation: {paper.reputation_score.toFixed(1)}
      </span>
    {:else}
      <!-- For OpenReview, we can show the conference category (e.g., "Oral") -->
      {#if paper.category}
        <span class="font-semibold bg-green-100 text-green-800 rounded-full px-3 py-1">
          {paper.category}
        </span>
      {/if}
    {/if}
    <span>{paper.year_or_date}</span>
  </div>
  
  <h2 class="text-xl font-bold text-slate-900 mb-2 leading-tight">
    <a href={paper.paper_url} target="_blank" rel="noopener noreferrer" class="hover:text-blue-600 transition-colors">
      {paper.title}
    </a>
  </h2>
  
  <p class="text-sm text-slate-600 italic mb-4">
    {paper.authors.join(', ')}
  </p>
  
  <!-- Use the prose class for nice abstract formatting -->
  {#if paper.abstract}
    <div class="prose prose-slate max-w-none text-slate-700 prose-p:my-2">
      <p>{paper.abstract}</p>
    </div>
  {/if}
  
  {#if paper.keywords && paper.keywords.length > 0}
    <div class="mt-4 flex flex-wrap gap-2">
      {#each paper.keywords as keyword}
        <span class="text-xs bg-slate-100 text-slate-700 rounded-full px-3 py-1">
          {keyword}
        </span>
      {/each}
    </div>
  {/if}

</article>