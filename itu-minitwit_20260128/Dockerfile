FROM python:3.9-slim

WORKDIR /app

# Create user first (better layer caching)
RUN useradd -m myuser

# Copy only necessary files (assuming you fix with .dockerignore)
COPY . .

# Install dependencies with pinned versions
RUN pip install --no-cache-dir \
    Flask==2.3.2 \
    Flask-PyMongo==2.3.0 \
    prometheus-flask-exporter==0.22.4 \
    blinker==1.6.2

# Create directory and set permissions in one layer
RUN mkdir -p /app/prometheus_metrics \
    && chown -R myuser:myuser /app

# Switch to non-root user
USER myuser

ENV PROMETHEUS_MULTIPROC_DIR=/app/prometheus_metrics

EXPOSE 5000

CMD ["python", "minitwit.py"]
