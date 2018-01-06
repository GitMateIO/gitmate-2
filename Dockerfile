FROM python:3-stretch
LABEL maintainer "Muhammad Kaisar Arkhan <yukinagato@protonmail.com>"

ENV USER=gitmate ROOT=/usr/src/app NUM_WORKERS=3 LOG_LEVEL=DEBUG TIMEOUT=30 MIN=3 MAX=10

EXPOSE 8000

WORKDIR $ROOT

RUN useradd -d $ROOT -r $USER

ADD . $ROOT

RUN set -ex && \
    \
    buildDeps=' \
        gcc \
        libpq-dev \
        libffi-dev \
    ' && \
    \
    apt-get update && \
    apt-get install -y --no-install-recommends apt-transport-https && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    echo \
    "deb [arch=amd64] https://download.docker.com/linux/debian stretch stable" \
    >> /etc/apt/sources.list && \
    \
    apt-get update && \
    apt-get install -y --no-install-recommends \
            libpq5 git docker-ce $buildDeps && \
    \
    pip install --no-cache-dir -r $ROOT/requirements.txt && \
    ./install_deps.sh && \
    \
    apt-get purge -y --auto-remove $buildDeps && \
    rm -rf /var/lib/apt/lists/*

CMD ["./docker/run.sh"]
