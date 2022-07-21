FROM python:3.10.1

ENV CONTAINER_HOME=/var/www/html

ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

RUN pip install -r  $CONTAINER_HOME/requirements.txt

CMD ["gunicorn", "--workers=3", "app.main:app"]