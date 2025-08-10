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
      
      const data = await response.json();
      
      // We need to transform the author data from [{'name': 'A'}, {'name': 'B'}] to ['A', 'B']
      // The DTO from the previous attempt is a better pattern, but this works directly.
      papers = data.map(paper => {
        return {
          ...paper,
          authors: paper.authors.map(author => author.name)
        };
      });

    } catch (e) {
      error = e.message;
    } finally {
      isLoading = false;
    }
  });
</script>

<main>
  <header>
    <h1>Frontier</h1>
    <p>The bleeding edge of AI research, sourced from arXiv.</p>
  </header>

  {#if isLoading}
    <p class="status">Loading latest papers...</p>
  {:else if error}
    <div class="status error">
      <p><strong>Could not fetch papers.</strong></p>
      <p>Error: {error}</p>
      <p>Please ensure the Litestar backend server is running at <code>http://127.0.0.1:8000</code>.</p>
    </div>
  {:else}
    <div class="paper-list">
      {#each papers as paper (paper.id)}
        <article class="paper-item">
          <p class="meta">
            <span>Submitted: {paper.submitted_date}</span>
          </p>
          <h2>
            <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">
              {paper.title}
            </a>
          </h2>
          <p class="authors">
            {paper.authors.join(', ')}
          </p>
          <p class="abstract">{paper.abstract}</p>
        </article>
      {/each}
    </div>
  {/if}
</main>

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
      
      const data = await response.json();
      
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

<!-- The HTML Structure is slightly improved with <header> and <section> for clarity -->
<main>
  <header class="site-header">
    <h1>Frontier</h1>
    <p>Your personal gateway to the bleeding edge of AI research.</p>
  </header>

  <section class="content">
    {#if isLoading}
      <div class="status-card">
        <p>Loading latest papers from arXiv...</p>
      </div>
    {:else if error}
      <div class="status-card error">
        <p><strong>Could Not Fetch Papers</strong></p>
        <p>Error: {error}</p>
        <p>Please ensure the backend server is running at <code>http://127.0.0.1:8000</code>.</p>
      </div>
    {:else}
      <div class="paper-list">
        {#each papers as paper (paper.id)}
          <article class="paper-card">
            <div class="card-header">
              <span class="score">Reputation: {paper.reputation_score.toFixed(1)}</span>
              <span class="date">Submitted: {paper.submitted_date}</span>
            </div>
            <h2 class="title">
              <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer">
                {paper.title}
              </a>
 