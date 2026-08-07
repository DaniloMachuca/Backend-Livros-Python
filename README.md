# Backend Livros Python

API simples para gerenciar um catálogo de livros com FastAPI, SQLAlchemy e SQLite.

## Requisitos

- Python 3.14 ou superior
- Poetry
- Docker e Docker Compose (opcional)

## Dependências

As dependências do projeto estão definidas em `pyproject.toml`:

- `fastapi[standard]`
- `sqlalchemy`
- `aiosqlite`

## Configuração

O projeto usa variáveis de ambiente, normalmente definidas em `.env`:

```env
USUARIO=admin
SENHA=admin
DATABASE_URL=sqlite:///./livros.db
PYTHONUNBUFFERED=1
```

A variável `DATABASE_URL` deve apontar para o banco de dados SQLite.

## Executando localmente

1. Instale as dependências com Poetry:

```bash
poetry install
```

2. Execute a aplicação:

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

3. Acesse a API em:

- `http://127.0.0.1:8000`
- Documentação automática: `http://127.0.0.1:8000/docs`

## Executando com Docker Compose

1. Construa e inicie o serviço:

```bash
docker-compose up --build
```

2. A API estará disponível em `http://127.0.0.1:8000`.

## Autenticação

A API usa autenticação HTTP Basic para todas as rotas de livros. Os valores são definidos em `.env` como `USUARIO` e `SENHA`.

## Endpoints principais

- `GET /livros` - lista livros
- `POST /adiciona` - adiciona livro
- `PUT /atualiza/{id_livro}` - atualiza livro
- `DELETE` não documentado mas mencionado no código como CRUD
- `GET /chamadas_externas` - simulação de chamadas externas assíncronas

## Observações

- O banco SQLite será criado automaticamente ao iniciar a aplicação.
- Caso use Docker, o volume `.:/app` garante que alterações no código sejam refletidas em tempo real.
