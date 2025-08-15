FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/backend"

WORKDIR /app/backend

COPY backend/requirements.txt /app/backend/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend /app/backend

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
