FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY ai_services/ ./ai_services

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 