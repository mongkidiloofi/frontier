<script>
  import { onMount } from 'svelte';

  let papers = [];
  let isLoading = true;
  let error = null;

  onMount(async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/papers/arxiv');
      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }
      
      let data = await response.json();
      
      // --- SORTING LOGIC ---
      // Sort the array by reputation_score in descending order (highest first).
      // The `|| 0` handles cases where the score might be null or undefined.
      data.sort((a, b) => (b.reputation_score || 0) - (a.reputation_score || 0));
      // --- END SORTING ---
      
      // Transform author data for easier display
      papers = data.map(paper => ({
        ...paper,
        authors: paper.authors.map(author => author.name)
      }));

    } catch (e) {
      error = e.message;
    } finally {
      isLoading = false;
    }
  });
</script>

<!-- 
  The HTML structure is now styled with Tailwind utility classes.
  Instead of a <style> block, the styles are applied directly to the elements.
-->
<body class="bg-slate-50 font-sans text-slate-800">
  <main class="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
    
    <header class="text-center pb-6 mb-8 border-b border-slate-200">
      <h1 class="text-4xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">Frontier</h1>
      <p class="mt-2 text-lg text-slate-600">The bleeding edge of AI research, ranked by reputation.</p>
    </header>

    <div>
      {#if isLoading}
        <div class="text-center py-12 text-slate-500">
          <p>Loading latest papers...</p>
        </div>
      {:else if error}
        <div class="bg-red-100 border border-red-300 text-red-800 rounded-lg p-6 text-center">
          <p class="font-bold">Could Not Fetch Papers</p>
          <p class="mt-2">Error: {error}</p>
        </div>
      {:else}
        <!-- space-y-8 adds vertical space between all child elements -->
        <div class="space-y-8">
          {#each papers as paper (paper.id)}
            <!-- A single paper "card" -->
            <article class="bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-lg hover:border-blue-400 transition-all duration-200 ease-in-out">
              
              <div class="flex justify-between items-center text-xs text-slate-500 mb-3">
                <span class="font-semibold bg-blue-100 text-blue-800 rounded-full px-3 py-1">
                  Reputation Score: {paper.reputation_score.toFixed(1)}
                </span>
                <span>Submitted: {paper.submitted_date}</span>
              </div>
              
              <h2 class="text-xl font-bold text-slate-900 mb-2 leading-tight">
                <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" class="hover:text-blue-600 transition-colors">
                  {paper.title}
                </a>
              </h2>
              
              <p class="text-sm text-slate-600 italic mb-4">
                {paper.authors.join(', ')}
              </p>
              
              <!-- The `prose` class from the typography plugin makes this look nice automatically -->
              <div class="prose prose-slate max-w-none text-slate-700">
                <p>{paper.abstract}</p>
              </div>

            </article>
          {/each}
        </div>
      {/if}
    </div>

  </main>
</body>