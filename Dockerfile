FROM python:3.13

ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONPATH=/app/src

WORKDIR /app
RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root --only main

COPY . .

#CMD ["uvicorn", "src.delivery.main:app", "--host", "0.0.0.0", "--port", "8000"]
