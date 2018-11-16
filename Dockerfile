FROM python:3.6-alpine
MAINTAINER Chris Kendall <ckendall@twilio.com>

ENV INSTALL_PATH /batchsms
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY Pipfile* ./
RUN pip install pipenv && pipenv install && pipenv install gunicorn redis

COPY batchsms/ .

CMD pipenv run ./batchsms/app.py