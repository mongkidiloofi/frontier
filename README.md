# Frontier 🚀

**Frontier** is a software engineering project designed to provide AI researchers with a streamlined platform for discovering and curating the latest research papers. It fetches pre-prints directly from arXiv, with future plans to integrate peer-reviewed sources like OpenReview, creating a single, powerful feed for the bleeding edge of AI research.

This project is being developed as part of the CSE470: Software Engineering course.

---

## ✨ Core Features (Sprint 1)

*   **Automated Data Ingestion:** A backend service automatically fetches the latest papers from the `cs.LG` (Machine Learning) category on arXiv.
*   **Robust Backend API:** A modern, asynchronous API built with **Litestar** serves the paper data as clean JSON.
*   **Professional Data Layer:** **SQLAlchemy** is used as an ORM to model and interact with a **PostgreSQL** database (hosted on Supabase), ensuring a clean separation of concerns.
*   **Organized Architecture:** The project strictly follows the **Model-View-Controller (MVC)** pattern, with a clear and scalable folder structure.

*Future sprints will introduce a Svelte frontend, user authentication, and a novel, community-driven tagging system for paper curation.*

---

## 🛠 Tech Stack

This project is built with a modern, asynchronous Python backend. The frontend will be developed separately with Svelte.

*   **Backend Framework:** [Litestar](https://litestar.dev/)
*   **Database:** [PostgreSQL](https://www.postgresql.org/) (hosted on [Supabase](https://supabase.com/))
*   **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (with `asyncpg` driver)
*   **API Documentation:** OpenAPI / Swagger UI (auto-generated)
*   **External Data Source:** [arXiv API](https://info.arxiv.org/help/api/index.html)

---

## 🏃‍♀️ Getting Started

Follow these instructions to set up and run the backend server locally.

### Prerequisites

*   Python 3.10+
*   A running PostgreSQL database (or a free Supabase project)

### 1. Clone the Repository

```bash
git clone https://github.com/mongkidiloofi/frontier.git
cd frontier
