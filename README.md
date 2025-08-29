# Frontier

![Stack](https://img.shields.io/badge/stack-Litestar_|_Svelte_|_Supabase-007aff.svg)

A minimalist, curated interface for the academic cutting-edge. Frontier fetches the latest papers from sources like arXiv and OpenReview, applies a unique ranking algorithm to surface the most relevant content, and provides a clean, fast, and focused reading experience.

## Core Features

-   **Dual Source Integration**: Fetches and unifies papers from **arXiv** and **OpenReview**.
-   **Bleeding-Edge Ranking**: A sophisticated, weighted algorithm that scores papers based on recency, reputation, and popularity (using a Wilson Score interval for statistical robustness).
-   **Interactive UI**: Users can vote on papers, add custom tags, and engage in discussions.
-   **Dynamic Filtering**: Filter the feed by source, tags, venue, year, and category.
-   **Performant by Design**: Built with a reactive, minimalist frontend featuring infinite scroll and optimistic updates for a fast, seamless experience.
-   **Clean Architecture**: A clear separation of concerns between the Litestar backend (API), the Svelte frontend (View), and the autonomous Svelte stores (State Management).

## Tech Stack

| Area      | Technology                                             |
| :-------- | :----------------------------------------------------- |
| **Backend** | [Litestar](https://litestar.dev/)                      |
|           | SQLAlchemy 2.0 (Async) with `asyncpg`                  |
| **Frontend**  | [Svelte](https://svelte.dev/) (no SvelteKit)           |
|           | TypeScript                                             |
|           | Vite                                                   |
| **Database**  | [Supabase](https://supabase.com/) (PostgreSQL)         |
