FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

RUN useradd -m myuser

COPY . .

RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir \
    Flask==3.1.3 \
    Flask-PyMongo \
    prometheus-flask-exporter \
    blinker

RUN mkdir -p /app/prometheus_metrics && \
    chown -R myuser:myuser /app

USER myuser

ENV PROMETHEUS_MULTIPROC_DIR=/app/prometheus_metrics

EXPOSE 5000

CMD ["python", "minitwit.py"]