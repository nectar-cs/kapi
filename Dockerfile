FROM python:3.6.1-alpine

RUN apk add --update git

WORKDIR /app

ADD . /app

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    REVISION=$REVISION \
    K8S_AUTH_TYPE=in \
    KAT_ENV=production \
    FLASK_ENV=production

RUN pip3 install pipenv
RUN pipenv install git+https://github.com/nectar-cs/k8-kat#egg=k8-kat
RUN pipenv install --deploy --ignore-pipfile

EXPOSE 5000

CMD ["pipenv", "run", "python3", "app.py"]