# API de livros

# GET, POST, PUT, DELETE

# POST - Adicionar novos livros (Create)
# GET - Buscar dados dos livros (Read)
# PUT - Atualizar informações dos livros (Update)
# DELETE - deletar informações dos livros (Delete)

# CRUD - Create, Read, Update, Delete

# Instalar o fastapi no Poetry: poetry add "fastapi[standard]"

# Endpoint: http://127.0.0.1:8000

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./livros.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



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

USUARIO = "admin"
SENHA = "admin"

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

def session_db():
     db = SessionLocal()
     try:
        yield db
     finally:
        db.close()
    

def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(credentials.username, USUARIO)
    is_password_correct = secrets.compare_digest(credentials.password, SENHA)

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
                status_code=401,
                detail="Usuário ou senha incorretos",
                headers={"WWW-Authenticate": "Basic"}
            )


@app.get("/livros")
def get_livros(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
    ):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Parâmetros de página e limite devem ser maiores que zero")

    livros_query = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()

    if not livros_query:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    
    total_livros = db.query(LivroDB).count()

    return {
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


@app.post("/adiciona")
def post_Livro(
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

    return {"message": "Livro adicionado com sucesso", "livro": livro}

@app.put("/atualiza/{id_livro}")
def put_Livro(
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

@app.delete("/deletar/{id_livro}")
def delete_Livro(
    id_livro: int,
    db: Session = Depends(session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
    ):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()

    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")

    db.delete(db_livro)
    db.commit()

    return {"message": "Livro deletado com sucesso"}
