FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install flask flask-pymongo pymongo werkzeug prometheus-flask-exporter

EXPOSE 5000

CMD ["python", "minitwit.py"]
