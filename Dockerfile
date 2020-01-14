FROM python:3.6.1-alpine

WORKDIR /app

ADD . /app

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    REVISION=$REVISION \
    CONNECT_AUTH_TYPE=in \
    KAT_ENV=production \
    FLASK_ENV=production

RUN pip3 install pipenv
RUN pipenv install --deploy --ignore-pipfile --sequential

EXPOSE 5000

CMD ["pipenv", "run", "python3", "app.py"]