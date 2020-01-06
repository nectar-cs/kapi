FROM python:3.6.1-alpine

WORKDIR /app

ADD . /app

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV REVISION $REVISION
ENV K8S_AUTH_TYPE=local
ENV FLASK_ENV=production

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0"]