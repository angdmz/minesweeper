FROM python:3.6.7-alpine
RUN apk add --no-cache git \
    build-base \
    postgresql \
    postgresql-dev \
    libpq
RUN mkdir -p /opt/project
WORKDIR /opt/project
ADD requirements.txt /opt/project
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install ipython
RUN pip install coverage
RUN pip install django-discover-runner
ADD . /opt/project