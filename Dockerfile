FROM python:3
MAINTAINER Muhammad Kaisar Arkhan <yukinagato@protonmail.com>

RUN apt-get update && apt-get install apt-transport-https ca-certificates curl gnupg2 software-properties-common -y && apt-get clean
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
RUN apt-get update && apt-get install docker-ce -y && apt-get clean

ENV USER=gitmate ROOT=/usr/src/app NUM_WORKERS=3 LOG_LEVEL=DEBUG TIMEOUT=30

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
