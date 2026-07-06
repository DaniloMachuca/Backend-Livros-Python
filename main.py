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
import os

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

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

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
def get_livros(page: int = 1, limit: int = 10, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Parâmetros de página e limite devem ser maiores que zero")

    if not livros:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")

    start = (page - 1) * limit
    end = start + limit

    livros_list = [
        {"id_livro": id_livro, "nome_livro": livro_data["nome_livro"], "autor_livro": livro_data["autor_livro"], "ano_livro": livro_data["ano_livro"]}
        for id_livro, livro_data in list(livros.items())[start:end]
    ]

    return {"page": page, "limit": limit, "livros": livros_list}


@app.post("/adiciona")
def post_Livro(id_livro: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if id_livro in livros:
        raise HTTPException(status_code=400, detail="Livro já existe")
    else:
        livros[id_livro] = livro.dict()
        return {"message": "Livro adicionado com sucesso", "livro": livros[id_livro]}

@app.put("/atualiza/{id_livro}")
def put_Livro(id_livro: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        livros[id_livro] = livro.dict()
        return {"message": "Livro atualizado com sucesso", "livro": livros[id_livro]}

@app.delete("/deletar/{id_livro}")
def delete_Livro(id_livro: int, credentials: HTTPBasicCredentials = Depends(autenticar_usuario)):
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        del livros[id_livro]
        return {"message": "Livro deletado com sucesso"}
