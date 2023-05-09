FROM python:3.11-slim-buster

RUN apt-get update && apt-get -y install curl

# install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"

COPY . /src
WORKDIR /src


RUN poetry install --only main
