FROM python:3.10-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

RUN apt update && apt install libmagic1 curl unzip -y
RUN poetry add python-magic

RUN curl https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip --output punkt.zip
RUN mkdir -p nltk_data/tokenizers/
RUN unzip punkt.zip
RUN mv punkt/ nltk_data/tokenizers/
RUN rm punkt.zip

COPY . .

EXPOSE 8000
EXPOSE 9200

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
