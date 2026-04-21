## V2.0
### 1. Created 'Dockerfile'
```dockerfile
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
```
### 2. Updated DB Path in 'minitwit.py'
Changed DB path to match the Docker WORKDIR /app for better data management.
```python
as-is : DATABASE = '/tmp/minitwit.db'
to-be : DATABASE = '/app/minitwit.db'
```
### 3. Initialized 'minitwit.db'
--------------------------------------
