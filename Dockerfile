# 1. based on python3
FROM python:3.11-slim

# 2. container
WORKDIR /app

# 3. install flask
RUN pip install flask

# 4. copy source code
COPY . .

# 5. Flask Port
EXPOSE 5000

# 6. Start server
CMD ["python", "minitwit.py"]
