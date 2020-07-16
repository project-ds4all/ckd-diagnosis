FROM python:3.7

LABEL maintainer = 'Juan Sebastian Hernandez <juans.hernandez@rappi.com>'

COPY . project/
WORKDIR project/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD sfx-py-trace server.py
