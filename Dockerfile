# Use official Python image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside backend
WORKDIR /app/backend

# Copy only requirements first for caching
COPY backend/requirements.txt /app/backend/

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the backend folder content
COPY backend /app/backend

# Expose Django port
EXPOSE 8000

# Run development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
