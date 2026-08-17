# Backend Books Python 📚

A lightweight API for managing a books catalog using **FastAPI**, **SQLAlchemy**, and **Redis** caching.

## ✨ Features

- RESTful API for book management (CRUD operations)
- HTTP Basic Authentication for protected routes
- Redis caching for improved performance
- Celery background tasks (sum, factorial calculations)
- Kafka event streaming and message production
- Asynchronous external API call simulation
- Docker & Docker Compose support
- Swagger UI documentation

## 📋 Requirements

- Python 3.10+ (tested with 3.11/3.12)
- Poetry
- Docker / Docker Compose

## 🔧 Environment Setup

Create a `.env` file with the following variables:

```env
USERNAME=admin
PASSWORD=admin
DATABASE_URL=sqlite:///./books.db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0
PYTHONUNBUFFERED=1
```

## 🚀 Quick Start

The recommended way to run this project is using Docker Compose:

```bash
docker-compose up --build
```

This will start all required services (API, Redis, Kafka, Kafka UI).

## 🌐 Access URLs

- **API Root**: http://127.0.0.1:8000
- **Swagger UI**: http://127.0.0.1:8000/docs
- **Kafka UI**: http://127.0.0.1:8080

## 🔐 Authentication

Management routes require HTTP Basic Authentication. Set your credentials in the `.env` file using `USERNAME` and `PASSWORD`.

## 📡 API Endpoints

### Books Management

- `GET /books` — List all books (supports `page` and `limit` query parameters)
- `POST /new-books` — Create a new book (body: `title`, `author`, `year`)
- `PUT /edit-book/{book_id}` — Update book by ID
- `DELETE /delete-book/{book_id}` — Delete book by ID

### Async Operations

- `GET /external-calls` — Simulated parallel external async calls

### Background Tasks (Celery)

- `POST /tasks/sum` — Start a sum task (query params: `num1`, `num2`)
- `POST /tasks/factorial` — Start a factorial task (query param: `n`)
- `GET /tasks/recent` — List recent Celery tasks (from Redis)

### Debug Utilities

- `GET /debug/redis` — Inspect Redis keys related to books

### Kafka Integration

- Kafka producer configured in `kafka_producer.py` for event streaming
- Messages can be published to Kafka topics for event-driven architecture

## 📝 Notes

- SQLite database is auto-created on first run when `DATABASE_URL` points to a local file
- Redis serves as a cache layer and stores Celery task IDs
- Celery tasks are defined in `tasks.py` (`sum_task`, `factorial_task`)
