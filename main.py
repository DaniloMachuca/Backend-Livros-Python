# API de livros

# GET, POST, PUT, DELETE

# POST - Adicionar novos livros (Create)
# GET - Buscar dados dos livros (Read)
# PUT - Atualizar informações dos livros (Update)
# DELETE - deletar informações dos livros (Delete)

# CRUD - Create, Read, Update, Delete

# Instalar o fastapi no Poetry: poetry add "fastapi[standard]"

# Endpoint: http://127.0.0.1:8000

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

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

livros = {}

# id do livro
# nome do livro
# autor do livro
# ano de lançamento do livro

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

@app.get("/livros")
def get_livros():
    if not livros:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    else:
        return {"livros": livros}

@app.post("/adiciona")
def post_Livro(id_livro: int, livro: Livro):
    if id_livro in livros:
        raise HTTPException(status_code=400, detail="Livro já existe")
    else:
        livros[id_livro] = livro.dict()
        return {"message": "Livro adicionado com sucesso", "livro": livros[id_livro]}

@app.put("/atualiza/{id_livro}")
def put_Livro(id_livro: int, livro: Livro):
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        livros[id_livro] = livro.dict()
        return {"message": "Livro atualizado com sucesso", "livro": livros[id_livro]}

@app.delete("/deletar/{id_livro}")
def delete_Livro(id_livro: int):
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        del livros[id_livro]
        return {"message": "Livro deletado com sucesso"}
