<script lang="ts">
  import Router from 'svelte-spa-router';
  import { routes } from './routes';
</script>

<main>
  <header>
    <h1>frontier</h1>
  </header>
  
  <Router {routes} />
</main>

<style>
  main {
    max-width: var(--container-width);
    margin: 0 auto;
    padding: var(--space-16) var(--space-4);
  }

  header h1 {
    font-size: var(--font-size-2xl);
    font-weight: 500;
    text-align: center;
    letter-spacing: 0.5px;
    margin-bottom: var(--space-16);
  }
</style>