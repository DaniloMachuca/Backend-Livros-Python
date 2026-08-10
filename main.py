# API de livros

# GET, POST, PUT, DELETE

# POST - Adicionar novos livros (Create)
# GET - Buscar dados dos livros (Read)
# PUT - Atualizar informações dos livros (Update)
# DELETE - deletar informações dos livros (Delete)

# CRUD - Create, Read, Update, Delete

# Instalar o fastapi no Poetry: poetry add "fastapi[standard]"

# Endpoint: http://127.0.0.1:8000

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
from tasks import somar, fatorial
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
    title = "Api de Livros",
    description = "Api para gerenciar catálogo de livros",
    version = "0.0.0",
    contact= {
        "name": "Danilo Machuca",
        "url": "https://github.com/DaniloMachuca",
        "email": "danilo.machuca.dev@gmail.com"
    }
)

USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")

security = HTTPBasic()

livros = {}

# id do livro
# nome do livro
# autor do livro
# ano de lançamento do livro

class LivroDB(Base):
    __tablename__ = "Livros"

    id = Column(Integer, primary_key=True, index=True)
    nome_livro = Column(String, index=True)
    autor_livro = Column(String, index=True)
    ano_livro = Column(Integer, index=True)

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

Base.metadata.create_all(bind=engine)

def salvar_livros_no_redis(livro_id: int, livro: Livro):
    redis_client.set(f"livro:{livro_id}", json.dumps(livro.dict()))

def deletar_livro_do_redis(livro_id: int):
    redis_client.delete(f"livro:{livro_id}")

def session_db():
     db = SessionLocal()
     try:
        yield db
     finally:
        db.close()
    
# Função para autenticar o usuário usando HTTP Basic Auth

def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, SENHA)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
                status_code=401,
                detail="Usuário ou senha incorretos",
                headers={"WWW-Authenticate": "Basic"}
            )

# Simulação de chamadas externas

async def chamadas_externas_1():
    await asyncio.sleep(2)
    return "Resultado da chamada externa 1"

async def chamadas_externas_2():
    await asyncio.sleep(2)
    return "Resultado da chamada externa 2"

async def chamadas_externas_3():
    await asyncio.sleep(2)
    return "Resultado da chamada externa 3"

@app.get("/chamadas_externas")
async def chamadas_externas():
    tarefa1 = asyncio.create_task(chamadas_externas_1())
    tarefa2 = asyncio.create_task(chamadas_externas_2())
    tarefa3 = asyncio.create_task(chamadas_externas_3())

    resultado1 = await tarefa1
    resultado2 = await tarefa2
    resultado3 = await tarefa3

    return {
        "message": "Chamadas externas concluidas",
        "chamada_1": resultado1,
        "chamada_2": resultado2,
        "chamada_3": resultado3
    }


# Tarefas assíncronas com Celery

@app.post("/calcular/soma")
def calcular_soma(num1: int, num2: int):
    tarefa = somar.delay(num1, num2)
    redis_client.lpush("tarefas_ids", tarefa.id)
    redis_client.ltrim("tarefas_ids", 0, 49)

    return {"task_id": tarefa.id, "message": "Tarefa de soma iniciada. Verifique o status da tarefa usando o task_id."}

@app.post("/calcular/fatorial")
def calcular_fatorial(n: int):
    tarefa = fatorial.delay(n)
    redis_client.lpush("tarefas_ids", tarefa.id)
    redis_client.ltrim("tarefas_ids", 0, 49)

    return {"task_id": tarefa.id, "message": "Tarefa de fatorial iniciada. Verifique o status da tarefa usando o task_id."}


@app.get("/tarefas/recentes")
def listar_tarefas_recentes():
    ids = redis_client.lrange("tarefas_ids", 0, -1)
    tarefas = []

    for task_id in ids:
        resultado = AsyncResult(task_id, app=celery_app)
        tarefas.append({
            "task_id": task_id,
            "status": resultado.status,
            "resultado": resultado.result if resultado.successful() else None
        })

    return {
        "message": "Lista de tarefas recentes",
        "tarefas": tarefas
    }

# Endpoint para verificar o status da tarefa no redis
@app.get("/debug/redis")
async def ver_livros_redis():
    chaves = redis_client.keys("livros:*")
    livros = []
    for chave in chaves:
        valor = redis_client.get(chave)
        ttl = redis_client.ttl(chave)
        livros.append({
            "chave": chave,
            "valor": json.loads(valor),
            "ttl": ttl
        })
    return livros


# Endpoint para buscar livros
@app.get("/livros")
async def get_livros(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
    ):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Parâmetros de página e limite devem ser maiores que zero")

    cache_key = f"livros:page={page}&limit={limit}"
    cached_livros = redis_client.get(cache_key)

    if cached_livros:
        return json.loads(cached_livros)

    livros_query = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()

    if not livros_query:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    
    total_livros = db.query(LivroDB).count()

    resposta = {
        "page": page,
        "limit": limit,
        "total": total_livros,
        "livros": [
            {
                "id": livro.id,
                "nome_livro": livro.nome_livro,
                "autor_livro": livro.autor_livro,
                "ano_livro": livro.ano_livro
            }
            for livro in livros_query
        ]
    }

    redis_client.setex(cache_key, 30, json.dumps(resposta))

    return resposta


# Endpoint para adicionar livros
@app.post("/adiciona")
async def post_Livro(
    livro: Livro,
    db: Session = Depends(session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
    ):
    db_livro = db.query(LivroDB).filter(LivroDB.nome_livro == livro.nome_livro, LivroDB.autor_livro == livro.autor_livro, LivroDB.ano_livro == livro.ano_livro).first()

    if db_livro:
        raise HTTPException(status_code=400, detail="Livro já existe no catálogo")

    novo_livro = LivroDB(
        nome_livro=livro.nome_livro,
        autor_livro=livro.autor_livro,
        ano_livro=livro.ano_livro
    )

    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    salvar_livros_no_redis(novo_livro.id, livro)

    return {"message": "Livro adicionado com sucesso", "livro": livro}

# Endpoint para atualizar livros
@app.put("/atualiza/{id_livro}")
async def put_Livro(
    id_livro: int,
    livro: Livro,
    db: Session = Depends(session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
    ):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()

    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    
    db_livro.nome_livro = livro.nome_livro
    db_livro.autor_livro = livro.autor_livro
    db_livro.ano_livro = livro.ano_livro

    db.commit()
    db.refresh(db_livro)

    return {"message": "Livro atualizado com sucesso", "livro": livro}

# Endpoint para deletar livros
@app.delete("/deletar/{id_livro}")
async def delete_Livro(
    id_livro: int,
    db: Session = Depends(session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
    ):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()

    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    db.delete(db_livro)
    db.commit()

    deletar_livro_do_redis(id_livro)

    return {"message": "Livro deletado com sucesso"}
