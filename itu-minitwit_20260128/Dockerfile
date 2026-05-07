FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir Flask Flask-PyMongo prometheus-flask-exporter blinker gunicorn

EXPOSE 5000

RUN mkdir -p /app/prometheus_metrics && chmod 755 /app/prometheus_metrics

RUN useradd -m myuser && chown -R myuser:myuser /app

USER myuser

ENV PROMETHEUS_MULTIPROC_DIR=/app/prometheus_metrics

CMD ["python3", "-m", "gunicorn", "--config", "gunicorn_config.py", "minitwit:app"]
