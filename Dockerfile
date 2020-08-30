FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -yq sqlite3 cron \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir /db
RUN /usr/bin/sqlite3 /db/weathermon.db

COPY ./requirements.txt requirements.txt
RUN python3.8 -m pip install --no-cache-dir -r requirements.txt

COPY ./app /app
COPY ./bin /app/bin

RUN python3.8 /app/bin/init_db.py
