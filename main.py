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

app = FastAPI()

livros = {}

@app.get("/livros")
def get_livros():
    if not livros:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado")
    else:
        return {"livros": livros}


# id do livro
# nome do livro
# autor do livro
# ano de lançamento do livro

@app.post("/adiciona")
def post_Livro(id_livro: int, nome_livro: str, autor_livro: str, ano_livro: int):
    if id_livro in livros:
        raise HTTPException(status_code=400, detail="Livro já existe")
    else:
        livros[id_livro] = {
            "nome_livro": nome_livro,
            "autor_livro": autor_livro,
            "ano_livro": ano_livro
        }
        return {"message": "Livro adicionado com sucesso", "livro": livros[id_livro]}

@app.put("/atualiza/{id_livro}")
def put_Livro(id_livro: int, nome_livro: str = None, autor_livro: str = None, ano_livro: int = None):
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        if nome_livro:
            livros[id_livro]["nome_livro"] = nome_livro
        if autor_livro:
            livros[id_livro]["autor_livro"] = autor_livro
        if ano_livro:
            livros[id_livro]["ano_livro"] = ano_livro
        return {"message": "Livro atualizado com sucesso", "livro": livros[id_livro]}

@app.delete("/deletar/{id_livro}")
def delete_Livro(id_livro: int):
    if id_livro not in livros:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    else:
        del livros[id_livro]
        return {"message": "Livro deletado com sucesso"}
