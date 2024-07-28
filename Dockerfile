FROM python:3.12-slim

LABEL authors="wladbelsky"

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app

WORKDIR /app

CMD ["python", "main.py"]
