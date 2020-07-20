FROM python:3.7

ENV PORT=80
LABEL maintainer = 'Juan Sebastian Hernandez <juanher94>'

COPY . /project/
WORKDIR /project/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE ${PORT}

CMD gunicorn --bind 0.0.0.0:${PORT} wsgi:app
