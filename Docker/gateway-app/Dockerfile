FROM python:3.11

COPY ./requirements.txt ./dependencies.txt
RUN pip install -r dependencies.txt
ADD src/ ./app/
WORKDIR /app

RUN pip install -r dependencies.txt
RUN chmod 777 start.sh

ENTRYPOINT ["/bin/sh", "start.sh"]