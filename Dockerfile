# Use official Python image
FROM python:3.11

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory to /app/backend
WORKDIR /app/backend

# Copy backend requirements
COPY backend/requirements.txt /app/backend/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy backend source code
COPY backend /app/backend

# Expose Django dev server port
EXPOSE 8000

# Start Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
