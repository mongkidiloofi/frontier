import { mount } from 'svelte';
import App from './App.svelte'; // <-- FIX: Import the actual App, not Home

const appRoot = document.getElementById('app');

if (!appRoot) {
  throw new Error("Fatal Error: The root element with id 'app' was not found in the DOM. The application cannot mount.");
}

const app = mount(App, {
  target: appRoot,
});

export default app;