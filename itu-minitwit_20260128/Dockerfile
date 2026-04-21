FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir Flask Flask-PyMongo prometheus-flask-exporter blinker
EXPOSE 5000
CMD ["python", "minitwit.py"]
RUN mkdir -p /tmp/prometheus_metrics && chmod 755 /tmp/prometheus_metrics
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_metrics
