FROM python:3.11-slim

WORKDIR /app/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app

EXPOSE 5000

CMD ["python", "-m", "backend.app"]
