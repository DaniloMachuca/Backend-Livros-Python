# Backend Books Python

Simple API to manage a books catalog using FastAPI, SQLAlchemy and Redis (cache).

**Requirements**

- Python 3.10+ (tested with 3.11/3.12)
- Poetry
- Docker / Docker Compose (optional)

**Environment variables (.env)**

```env
USERNAME=admin
PASSWORD=admin
DATABASE_URL=sqlite:///./books.db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0
PYTHONUNBUFFERED=1
```

**Local installation**

```bash
poetry install
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Running with Docker Compose**

```bash
docker-compose up --build
```

**Useful URLs**

- API root: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

**Authentication**
The management routes use HTTP Basic. Configure `USERNAME` and `PASSWORD` in the `.env` file.

**Main endpoints**

- `GET /books` — List books (supports `page` and `limit` query params)
- `POST /books` — Create a new book (body: `title`, `author`, `year`)
- `PUT /books/{book_id}` — Update book by id
- `DELETE /books/{book_id}` — Delete book by id
- `GET /external-calls` — Simulated parallel external async calls
- `POST /tasks/sum` — Start background Celery sum task (query params `num1` and `num2`)
- `POST /tasks/factorial` — Start background Celery factorial task (query param `n`)
- `GET /tasks/recent` — List recent Celery tasks (reads IDs from Redis)
- `GET /debug/redis` — Inspect Redis keys related to books

**Notes**

- The SQLite database file is created automatically on first run when `DATABASE_URL` points to a local file.
- Redis is used as a cache and to store a list of Celery task IDs.
- The Celery tasks are in `tasks.py` (`sum_task`, `factorial_task`).

All routes, model names and environment variables in this README are in English.
