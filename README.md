# Frontier

Frontier is a modern web application designed to help AI researchers discover and evaluate the latest pre-print research papers. It ingests papers from arXiv and enriches them with a reputation score calculated from the authors' publication history in top-tier venues, powered by the Semantic Scholar API.

This project is developed with a strict, decoupled Model-View-Controller (MVC) architecture, featuring a Python backend and a Svelte frontend.

## Key Features

-   **Automated Data Ingestion**: A background service fetches the latest papers from a comprehensive set of AI/ML categories on arXiv.
-   **Reputation Scoring**: A robust service analyzes each paper's authors and calculates a reputation score based on their publication history in elite, peer-reviewed conferences and journals.
-   **High-Performance API**: An asynchronous backend built with Litestar serves the enriched and ranked paper data as a clean JSON API.
-   **Decoupled Frontend**: A reactive and responsive user interface built with Svelte and styled with Tailwind CSS provides a clean, sorted view of the most impactful new research.

## Tech Stack

| Layer              | Technology                                                                                                  |
| :----------------- | :---------------------------------------------------------------------------------------------------------- |
| **Frontend (View)**    | [Svelte](https://svelte.dev/) + [Vite](https://vitejs.dev/) + [Tailwind CSS](https://tailwindcss.com/)      |
| **Backend (Controller)**| [Litestar](https://litestar.dev/) on [Uvicorn](https://www.uvicorn.org/)                                  |
| **ORM (Model)**      | [SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/)                                                       |
| **Database**         | [PostgreSQL](https://www.postgresql.org/) (hosted on [Supabase](https://supabase.com/))                            |
| **Data Sources**     | [arXiv API](https://info.arxiv.org/help/api/index.html), [Semantic Scholar API](https://www.semanticscholar.org/product/api) |

## Local Development Setup

### Prerequisites

-   Python 3.10+
-   Node.js v20.x+
-   A PostgreSQL database (a free Supabase project is recommended)

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
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt 
# (If requirements.txt is unavailable, run: pip install litestar uvicorn "sqlalchemy[asyncio]" asyncpg python-dotenv arxiv httpx)
```

**Environment Configuration:**

Create a `.env` file in the `backend/` directory. Use the **Session Pooler** credentials from your Supabase project. An API key for Semantic Scholar is optional but highly recommended to avoid rate-limiting.

```.env
# backend/.env
user=postgres.your-project-ref
password=YOUR_DB_PASSWORD
host=aws-0-region-1.pooler.supabase.com
port=5432
dbname=postgres
SEMANTIC_SCHOLAR_API_KEY="YOUR_API_KEY_HERE"
```

**Database Initialization:**

```bash
# Create the database tables
python create_tables.py

# Fetch papers and calculate reputation scores (this is a long-running process)
python -m services.arxiv_fetcher
```

**Run the Backend Server:**

```bash
litestar --app main:app run --reload --debug
```
The API is now available at `http://127.0.0.1:8000`.

### 3. Frontend Setup

In a **new terminal**, run all frontend commands from the `frontend/` directory.

```bash
# Navigate to the frontend
cd frontend

# Install Node.js dependencies
npm install

# Run the frontend development server
npm run dev
```
The application is now accessible at `http://localhost:5173`.

## API Endpoints

-   `GET /api/papers/arxiv`: Retrieves a list of recent arXiv papers, sorted by reputation score.
-   `GET /schema/swagger`: View and interact with the live, auto-generated API documentation.
