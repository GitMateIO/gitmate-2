FROM frolvlad/alpine-python-machinelearning:latest
MAINTAINER Muhammad Kaisar Arkhan <yukinagato@protonmail.com>

ENV USER=gitmate ROOT=/usr/src/app NUM_WORKERS=3 LOG_LEVEL=DEBUG TIMEOUT=30

EXPOSE 8000

WORKDIR $ROOT

RUN addgroup -S $USER && \
    adduser -h $ROOT -G $USER -S $USER

ADD requirements.txt $ROOT/

RUN apk add --no-cache docker postgresql-libs && \
    apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        postgresql-dev \
        python3-dev && \
    pip install --no-cache-dir -r $ROOT/requirements.txt && \
    python3 -m nltk.downloader -d /usr/local/share/nltk_data averaged_perceptron_tagger wordnet stopwords && \
    apk del .build-deps

ADD . $ROOT

CMD ["./docker/run.sh"]
