# Frontier 🚀

A backend API to fetch and serve the latest research papers from arXiv.

### Stack

-   **Framework**: Litestar
-   **Database**: PostgreSQL (Supabase)
-   **ORM**: SQLAlchemy
-   **Async Driver**: `asyncpg`

---

### Quick Start

1.  **Clone & Setup Environment**
    ```bash
    git clone https://github.com/mongkidiloofi/frontier.git
    cd frontier
    python3 -m venv venv
    source venv/bin/activate
    pip install litestar uvicorn "sqlalchemy[asyncio]" asyncpg python-dotenv arxiv
    ```

2.  **Configure Database**
    -   Create a `.env` file in the project root.
    -   Add your Supabase **Session Pooler** credentials to it.

3.  **Initialize & Populate Database**
    ```bash
    # Create the database tables
    python create_tables.py

    # Fetch papers from arXiv
    python -m services.arxiv_fetcher
    ```

4.  **Run Server**
    ```bash
    litestar --app main:app run --reload --debug
    ```

---

### API Endpoints

-   `GET /api/papers/arxiv` - Fetches recent arXiv papers.
-   `GET /schema/swagger` - Interactive API documentation.

The server is now running at `http://127.0.0.1:8000`.
