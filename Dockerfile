FROM python:3-alpine
MAINTAINER Muhammad Kaisar Arkhan <yukinagato@protonmail.com>

ENV USER=gitmate ROOT=/usr/src/app NUM_WORKERS=3 LOG_LEVEL=DEBUG TIMEOUT=30

EXPOSE 8000

ADD requirements.txt $ROOT/

RUN apk add --no-cache docker postgresql-libs && \
    apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        postgresql-dev \
        python3-dev && \
    pip install --no-cache-dir -r $ROOT/requirements.txt && \
    apk del .build-deps

ADD . $ROOT

RUN addgroup -S $USER && \
    adduser -h $ROOT -G $USER -S $USER

WORKDIR $ROOT
CMD ["./docker/run.sh"]
