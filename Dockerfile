FROM python:3.6-alpine



RUN adduser -D microblog



WORKDIR /Desktop/quantamix/microblog

COPY requirements requirements
RUN apk add --update --no-cache --virtual build-deps  build-base gcc python3-dev musl-dev libc-dev linux-headers libxslt-dev libxml2-dev git bash sudo  py2-pip jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev python \
&& apk add libffi-dev openssl-dev
RUN python -m venv venv
RUN pip install -U setuptools
RUN python -m pip install --upgrade pip
RUN venv/bin/pip install -r requirements/docker.txt



RUN venv/bin/pip install gunicorn


COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP microblog.py
ENV FLASK_CONFIG docker

RUN chown -R microblog:microblog ./
USER microblog


# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
