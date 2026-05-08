FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && \
    apt-get upgrade -y libssl3t64 openssl && \
    rm -rf /var/lib/apt/lists/*
COPY . .
RUN pip install --no-cache-dir --only-binary :all: blinker==1.8.2 Flask==3.0.3 Flask-PyMongo==2.3.0 gunicorn==22.0.0 prometheus-flask-exporter==0.23.0
EXPOSE 5000
RUN mkdir -p /app/prometheus_metrics && \
    useradd -m myuser && \
    chown -R myuser:myuser /app && \
    chmod 755 /app/prometheus_metrics
USER myuser
ENV PROMETHEUS_MULTIPROC_DIR=/app/prometheus_metrics
CMD ["python3", "-m", "gunicorn", "--config", "gunicorn_config.py", "minitwit:app"]