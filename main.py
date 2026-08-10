"""
Books API

Supports basic CRUD operations for a books catalog.

Endpoints implement Create, Read, Update and Delete operations.

Install dependencies with Poetry: poetry add "fastapi[standard]"

Service endpoint: http://127.0.0.1:8000
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import os
import asyncio
import redis
import json
from dotenv import load_dotenv
from tasks import sum_task, factorial_task
from celery_app import celery_app
from celery.result import AsyncResult

load_dotenv()

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

app = FastAPI(
    title = "Books API",
    description = "API to manage a books catalog",
    version = "0.0.0",
    contact= {
        "name": "Danilo Machuca",
        "url": "https://github.com/DaniloMachuca",
        "email": "danilo.machuca.dev@gmail.com"
    }
)

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

security = HTTPBasic()

books_cache = {}

class BookDB(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    year = Column(Integer, index=True)


class Book(BaseModel):
    title: str
    author: str
    year: int

Base.metadata.create_all(bind=engine)

def save_book_to_redis(book_id: int, book: Book):
    """Save a book payload to Redis (simple cache).

    Key format: "book:<id>".
    """
    redis_client.set(f"book:{book_id}", json.dumps(book.dict()))

def delete_book_from_redis(book_id: int):
    """Delete a book entry from Redis by id."""
    redis_client.delete(f"book:{book_id}")

def get_db():
    """Database session dependency.

    Yields a SQLAlchemy session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    """Authenticate incoming requests using HTTP Basic credentials.

    Raises HTTPException(401) when credentials are invalid.
    """
    is_username_correct = secrets.compare_digest(credentials.username, USERNAME)
    is_password_correct = secrets.compare_digest(credentials.password, PASSWORD)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"}
        )

# Simulated external calls (async)

async def external_call_1():
    await asyncio.sleep(2)
    return "Result of external call 1"

async def external_call_2():
    await asyncio.sleep(2)
    return "Result of external call 2"

async def external_call_3():
    await asyncio.sleep(2)
    return "Result of external call 3"

@app.get("/external-calls")
async def external_calls():
    """Trigger several simulated external async calls in parallel."""
    task1 = asyncio.create_task(external_call_1())
    task2 = asyncio.create_task(external_call_2())
    task3 = asyncio.create_task(external_call_3())

    result1 = await task1
    result2 = await task2
    result3 = await task3

    return {
        "message": "External calls completed",
        "call_1": result1,
        "call_2": result2,
        "call_3": result3
    }


# Asynchronous background tasks (Celery)

@app.post("/tasks/sum")
async def start_sum_task(num1: int, num2: int):
    """Start an asynchronous sum task via Celery and return the task id."""
    task = sum_task.delay(num1, num2)
    redis_client.lpush("task_ids", task.id)
    redis_client.ltrim("task_ids", 0, 49)

    return {"task_id": task.id, "message": "Sum task started. Check status with the task_id."}

@app.post("/tasks/factorial")
async def start_factorial_task(n: int):
    """Start an asynchronous factorial task via Celery and return the task id."""
    task = factorial_task.delay(n)
    redis_client.lpush("task_ids", task.id)
    redis_client.ltrim("task_ids", 0, 49)

    return {"task_id": task.id, "message": "Factorial task started. Check status with the task_id."}


@app.get("/tasks/recent")
async def list_recent_tasks():
    """Return recent Celery tasks stored in Redis with basic status info."""
    ids = redis_client.lrange("task_ids", 0, -1)
    tasks_list = []

    for task_id in ids:
        result = AsyncResult(task_id, app=celery_app)
        tasks_list.append({
            "task_id": task_id,
            "status": result.status,
            "result": result.result if result.successful() else None
        })

    return {
        "message": "Recent tasks",
        "tasks": tasks_list
    }

# Endpoint to inspect Redis keys and cache
@app.get("/debug/redis")
async def debug_redis():
    """Inspect Redis keys related to books for debugging purposes."""
    keys = redis_client.keys("books:*")
    items = []
    for key in keys:
        value = redis_client.get(key)
        ttl = redis_client.ttl(key)
        items.append({
            "key": key,
            "value": json.loads(value) if value else None,
            "ttl": ttl
        })
    return items


# Endpoint to list books
@app.get("/books")
async def get_books(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(authenticate_user)
    ):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Page and limit must be greater than zero")

    cache_key = f"books:page={page}&limit={limit}"
    cached_books = redis_client.get(cache_key)

    if cached_books:
        return json.loads(cached_books)

    books_query = db.query(BookDB).offset((page - 1) * limit).limit(limit).all()

    if not books_query:
        raise HTTPException(status_code=404, detail="No books found")
    
    total_books = db.query(BookDB).count()

    resposta = {
        "page": page,
        "limit": limit,
        "total": total_books,
        "books": [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "year": book.year
            }
            for book in books_query
        ]
    }

    redis_client.setex(cache_key, 30, json.dumps(resposta))

    return resposta


# Endpoint to create a book
@app.post("/books")
async def create_book(
    book: Book,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(authenticate_user)
    ):
    db_book = db.query(BookDB).filter(BookDB.title == book.title, BookDB.author == book.author, BookDB.year == book.year).first()

    if db_book:
        raise HTTPException(status_code=400, detail="Book already exists in the catalog")

    new_book = BookDB(
        title=book.title,
        author=book.author,
        year=book.year
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    save_book_to_redis(new_book.id, book)

    return {"message": "Book added successfully", "book": book}

# Endpoint to update a book
@app.put("/books/{book_id}")
async def update_book(
    book_id: int,
    book: Book,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(authenticate_user)
    ):
    db_book = db.query(BookDB).filter(BookDB.id == book_id).first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_book.title = book.title
    db_book.author = book.author
    db_book.year = book.year

    db.commit()
    db.refresh(db_book)

    return {"message": "Book updated successfully", "book": book}

# Endpoint to delete a book
@app.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPBasicCredentials = Depends(authenticate_user)
    ):
    db_book = db.query(BookDB).filter(BookDB.id == book_id).first()

    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()

    delete_book_from_redis(book_id)

    return {"message": "Book deleted successfully"}
