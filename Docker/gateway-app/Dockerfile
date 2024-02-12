FROM python:3.11

COPY app-files /app
WORKDIR /app

RUN pip install -r dependencies.txt
RUN chmod 777 start.sh

ENTRYPOINT ["/bin/sh", "start.sh"]