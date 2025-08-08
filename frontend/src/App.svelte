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

<style>
  /* A modern CSS reset and font settings */
  :global(html) {
    box-sizing: border-box;
    font-size: 16px;
  }
  :global(*, *:before, *:after) {
    box-sizing: inherit;
  }
  :global(body) {
    margin: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background-color: #f7f7f7; /* Light, neutral gray background */
    color: #2c3e50; /* Dark slate text for high readability */
    line-height: 1.6;
  }
  /* Import the 'Inter' font from Google Fonts */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

  /* Main content container */
  main {
    max-width: 800px;
    margin: 2rem auto;
    padding: 1rem;
  }

  /* Header section */
  header {
    text-align: center;
    margin-bottom: 3rem;
  }

  h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a202c;
    margin: 0 0 0.5rem 0;
  }

  header p {
    font-size: 1.1rem;
    color: #718096; /* A softer gray */
    margin-top: 0;
  }
  
  /* Status messages (Loading/Error) */
  .status {
    text-align: center;
    padding: 2rem;
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    color: #4a5568;
  }
  .error {
    color: #c53030;
    background-color: #fff5f5;
    border-color: #fed7d7;
  }

  /* Paper List */
  .paper-list {
    list-style: none;
    padding: 0;
  }

  /* Individual Paper Item */
  .paper-item {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    transition: border-color 0.2s ease-in-out;
  }

  .paper-item:hover {
    border-color: #3498db; /* A nice blue border on hover */
  }
  
  .meta {
    font-size: 0.85rem;
    color: #718096;
    margin-bottom: 1rem;
  }
  
  /* Paper title */
  .paper-item h2 {
    font-size: 1.4rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
    line-height: 1.3;
  }

  .paper-item h2 a {
    text-decoration: none;
    color: #2980b9; /* A professional, accessible blue */
  }

  .paper-item h2 a:hover {
    text-decoration: underline;
  }

  /* Author list */
  .authors {
    font-size: 0.95rem;
    color: #555;
    margin-bottom: 1.25rem;
  }

  /* Abstract */
  .abstract {
    font-size: 1rem;
    color: #34495e; /* A slightly softer dark slate for body text */
    padding-left: 1rem;
    border-left: 3px solid #e2e8f0;
  }
</style>