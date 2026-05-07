FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && \
    apt-get upgrade -y libssl3t64 openssl && \
    rm -rf /var/lib/apt/lists/*
COPY . .
RUN pip install --no-cache-dir --only-binary :all: \
    Flask==1.8.2 \ 
    Flask-PyMongo==2.3.0 \ 
    prometheus-flask-exporter==0.23.0 \
    blinker==1.8.2 \
    gunicorn==22.0.0
EXPOSE 5000
RUN mkdir -p /app/prometheus_metrics && chmod 755 /app/prometheus_metrics
RUN useradd -m myuser && chown -R myuser:myuser /app
USER myuser
ENV PROMETHEUS_MULTIPROC_DIR=/app/prometheus_metrics
CMD ["python3", "-m", "gunicorn", "--config", "gunicorn_config.py", "minitwit:app"]