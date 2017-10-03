FROM frolvlad/alpine-python-machinelearning:latest
LABEL maintainer "Muhammad Kaisar Arkhan <yukinagato@protonmail.com>"

ENV USER=gitmate ROOT=/usr/src/app NUM_WORKERS=3 LOG_LEVEL=DEBUG TIMEOUT=30

EXPOSE 8000

WORKDIR $ROOT

RUN addgroup -S $USER && \
    adduser -h $ROOT -G $USER -S $USER

ADD . $ROOT

RUN apk add --no-cache docker postgresql-libs git && \
    apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        postgresql-dev \
        python3-dev && \
    pip install --no-cache-dir -r $ROOT/requirements.txt && \
    ./.ci/install_ee_deps.sh && \
    apk del .build-deps

CMD ["./docker/run.sh"]
