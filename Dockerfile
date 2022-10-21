FROM python:3.10

RUN mkdir -p /src

COPY cazycrawler /src/cazycrawler
COPY requirements.txt /src/

RUN pip install -r /src/requirements.txt

WORKDIR /src/cazycrawler/

CMD scrapy crawl cazy_classes -o /output/cazy.jsonlines