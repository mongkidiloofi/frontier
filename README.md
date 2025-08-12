# Frontier 🚀

Frontier is a software engineering project designed to provide AI researchers with a streamlined and curated platform for discovering the latest research papers. It features two distinct feeds:

1.  **A "Bleeding Edge" Pre-print Feed:** Ingests the latest papers from arXiv and enriches them with a reputation score. The score is calculated by analyzing the authors' publication history in top-tier venues, powered by the Semantic Scholar API.
2.  **A "Peer-Reviewed" Conference Feed:** Builds a comprehensive database of all papers from elite, peer-reviewed conferences and journals hosted on OpenReview, such as ICLR, NeurIPS, and ICML.

This project is developed with a strict, decoupled Model-View-Controller (MVC) architecture.

## Key Features

-   **Dual Data Pipelines**: Two independent services fetch and process data from both the arXiv and OpenReview APIs.
-   **Intelligent Reputation Ranking**: The arXiv feed is automatically sorted by a calculated reputation score, surfacing the most potentially impactful research first.
-   **High-Performance API**: An asynchronous backend built with Litestar serves the enriched and ranked paper data as a clean JSON API.
-   **Decoupled Frontend**: A reactive and responsive user interface built with Svelte and styled with Tailwind CSS provides a clean, tabbed view of the two distinct data feeds.
-   **Professional-Grade Data Layer**: SQLAlchemy 2.0 (Async) is used as an ORM to model and interact with a PostgreSQL database.

## Tech Stack

| Layer                | Technology                                                                                                                              |
| :------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontend (View)**      | [Svelte](https://svelte.dev/) + [Vite](https://vitejs.dev/) + [Tailwind CSS](https://tailwindcss.com/)                                    |
| **Backend (Controller)** | [Litestar](https://litestar.dev/) on [Uvicorn](https://www.uvicorn.org/)                                                                |
| **ORM (Model)**        | [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/)                                                                                   |
| **Database**           | [PostgreSQL](https://www.postgresql.org/) (hosted on [Supabase](https://supabase.com/))                                                        |
| **Data Sources**       | [arXiv API](https://info.arxiv.org/help/api/index.html), [OpenReview API](https://openreview-py.readthedocs.io/en/latest/), [Semantic Scholar API](https://www.semanticscholar.org/product/api) |
| **Runtime**            | Python 3.10+, Node.js 20+                                                                                                               |

## Local Development Setup

### Prerequisites

-   Python 3.10+
-   Node.js v20.x+
-   A PostgreSQL database (a free Supabase project is recommended)
-   An OpenReview account (for credentials)

### 1. Clone the Repository

```bash
git clone https://github.com/mongkidiloofi/frontier.git
cd frontier
```

### 2. Backend Setup

All backend commands should be run from the `backend/` directory.

```bash
# Navigate to the backend
cd backend

# Create and activate a Python virtual environment
python3 -m venv ven
source venv/bin/activate

# Install Python dependencies
pip install litestar uvicorn "sqlalchemy[asyncio]" asyncpg python-dotenv arxiv openreview-py psycopg2-binary httpx pandas```

**Environment Configuration:**

Create a `.env` file in the `backend/` directory. Use the **Session Pooler** credentials from Supabase.

```.env
# backend/.env
user=postgres.your-project-ref
password=YOUR_DB_PASSWORD
host=aws-0-region-1.pooler.supabase.com
port=5432
dbname=postgres

# Your OpenReview credentials
OPENREVIEW_USER="your-openreview-email@example.com"
OPENREVIEW_PASS="your_openreview_password"

# Optional but recommended
SEMANTIC_SCHOLAR_API_KEY="YOUR_API_KEY_HERE" 
```

**Database Initialization:**

```bash
# Create the unified 'papers' table in your database
python create_tables.py

# Fetch papers from arXiv and OpenReview.
# Note: This is a long-running process that makes many API calls.
python -m services.arxiv_fetcher
python -m services.openreview_fetcher
```

**Run the Backend Server:**

```bash
litestar --app main:app run --reload --debug
```
The backend API is now available at `http://127.0.0.1:8000`.

### 3. Frontend Setup

In a **new terminal window**, run all frontend commands from the `frontend/` directory.

```bash
# Navigate to the frontend from the project root
cd frontend

# Install Node.js dependencies
npm install

# Run the frontend development server
npm run dev
```
The application is now accessible at `http://localhost:5173`.

## API Endpoints

-   `GET /api/papers/arxiv`: Retrieves recent arXiv papers, sorted by reputation.
-   `GET /api/papers/openreview`: Retrieves recent OpenReview papers, sorted by date.
-   `GET /schema/swagger`: View and interact with the live, auto-generated API documentation.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## Data Attribution

This project builds upon the fantastic work of several open data platforms in the academic community.
-   Paper pre-prints are sourced from the **arXiv API**.
-   Conference and journal data is sourced from the **OpenReview API**.
-   Author reputation data is powered by the **Semantic Scholar API** from the Allen Institute for AI.
