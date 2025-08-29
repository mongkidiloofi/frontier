import Home from './pages/Home.svelte';
import { wrap } from 'svelte-spa-router/wrap'

export const routes = {
  '/': Home,
  
  // Dynamic imports for code splitting
  '/paper/:id': wrap({
    asyncComponent: () => import('./pages/PaperDetail.svelte')
  }),

  // Catch-all for 404
  '*': wrap({
    asyncComponent: () => import('./pages/NotFound.svelte')
  }),
};