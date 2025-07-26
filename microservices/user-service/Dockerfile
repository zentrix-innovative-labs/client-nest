# Use Python base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the Django port
EXPOSE 8000

# Set environment variables (optional for dev)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

