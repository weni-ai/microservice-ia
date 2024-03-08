FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

RUN apt update && apt install libmagic1 -y
RUN poetry add python-magic

COPY . .

EXPOSE 8000
EXPOSE 9200

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
