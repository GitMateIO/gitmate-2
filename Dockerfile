FROM coala/base:0.10
MAINTAINER Muhammad Kaisar Arkhan <yukinagato@protonmail.com>

ENV USER=gitmate ROOT=/usr/src/app NUM_WORKERS=3 LOG_LEVEL=DEBUG

EXPOSE 8000

RUN groupadd -r $USER && \
    useradd -r -m --home-dir=$ROOT -s /usr/sbin/nologin \
    -g $USER $USER

ADD requirements.txt $ROOT/
RUN pip3 install --no-cache-dir \
                 -r $ROOT/requirements.txt

ADD . $ROOT
WORKDIR $ROOT

RUN touch db.sqlite3 && \
    chown $USER:$USER db.sqlite3

CMD ["./docker/run.sh"]
