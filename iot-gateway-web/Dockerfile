FROM python:3.9-slim-buster

RUN apt-get update && apt-get -y install curl

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

COPY . /src
WORKDIR /src

RUN poetry install --only main

CMD cd src && poetry run uvicorn --host 0.0.0.0 --port 8000 main:app
