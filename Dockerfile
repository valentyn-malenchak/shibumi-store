# Requirements stage
FROM python:3.12-slim as requirements-stage

WORKDIR /tmp

RUN pip install poetry==1.7.1

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Building application container
FROM python:3.12-slim

WORKDIR /src

COPY --from=requirements-stage /tmp/requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY . /src

CMD ["invoke", "run"]
