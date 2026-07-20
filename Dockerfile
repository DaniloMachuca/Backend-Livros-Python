FROM python:3.14-rc-slim

WORKDIR /app

RUN pip install "poetry"

COPY pyproject.toml poetry.lock ./

ENV POETRY_HTTP_TIMEOUT=120
ENV PIP_DEFAULT_TIMEOUT=120

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]