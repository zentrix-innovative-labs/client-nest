# Analytics Service

The **Analytics Service** is a core microservice in the ClientNest platform, responsible for collecting, processing, and serving analytics data. It provides RESTful APIs for dashboards, engagement, audience insights, custom reports, and more. The service is built with Django and Django REST Framework, supporting JWT authentication and comprehensive OpenAPI documentation.

---

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Requirements](#requirements)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the Service](#running-the-service)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [API Documentation](#api-documentation)
- [Health Check](#health-check)
- [Static Files](#static-files)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contribution Guidelines](#contribution-guidelines)
- [License](#license)

---

## Overview

The Analytics Service enables data-driven insights for the ClientNest platform. It aggregates and analyzes data from various sources, exposing endpoints for:
- Real-time dashboards
- User engagement metrics
- Audience analytics
- Custom and scheduled reports
- AI usage and performance metrics

It is designed for scalability, security, and easy integration with other microservices.

---

## Architecture

- **Framework:** Django, Django REST Framework
- **API Auth:** JWT (djangorestframework-simplejwt)
- **API Docs:** drf-yasg & drf-spectacular (Swagger, Redoc, OpenAPI)
- **Modular Apps:**
  - `performance` (performance analytics)
  - `ai_usage` (AI usage tracking)
  - `reports` (reporting)
  - `metrics` (metrics aggregation)
- **Static Files:** Served from `/static/`, collected in `staticfiles/`

**Diagram:**
```
[Client] ⇄ [API Gateway] ⇄ [Analytics Service]
                                 ↑
         [Other Microservices] --|
```

---

## Features
- Analytics dashboards and reports
- Engagement and audience insights
- Custom report generation
- JWT-based authentication
- OpenAPI/Swagger/Redoc documentation
- Health check endpoint
- Modular, extensible design

---

## Requirements
- Python 3.8+
- Django 3.2+
- Django REST Framework
- drf-yasg, drf-spectacular
- djangorestframework-simplejwt
- (See `requirements.txt` for full list)

---

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd microservices/analytics-service
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

---

## Configuration

Configuration is managed via environment variables or a `.env` file. Key variables include:

- `DJANGO_SECRET_KEY` – Secret key for Django
- `DEBUG` – Set to `False` in production
- `DATABASE_URL` – Database connection string
- `ALLOWED_HOSTS` – Comma-separated list of allowed hosts
- (Add any other relevant variables as needed)

---

## Running the Service

Start the development server:
```bash
python manage.py runserver
```
The service will be available at [http://localhost:8000/](http://localhost:8000/).

---

## API Endpoints

| Endpoint                                 | Description                        | Auth Required |
|-------------------------------------------|------------------------------------|--------------|
| `/admin/`                                | Django admin panel                 | Yes          |
| `/health/`                               | Health check                       | No           |
| `/dashboard/`                            | Analytics dashboard                | Yes          |
| `/engagement/`                           | Engagement analytics               | Yes          |
| `/audience/`                             | Audience analytics                 | Yes          |
| `/custom-report/`                        | Custom report generation           | Yes          |
| `/insights/`                             | Insights analytics                 | Yes          |
| `/api/v1/analytics/performance/`         | Performance analytics (sub-app)    | Yes          |
| `/api/v1/analytics/ai-usage/`            | AI usage analytics (sub-app)       | Yes          |
| `/api/v1/analytics/reports/`             | Reports (sub-app)                  | Yes          |
| `/api/v1/analytics/metrics/`             | Metrics (sub-app)                  | Yes          |
| `/api/token/`                            | Obtain JWT token                   | No           |
| `/api/token/refresh/`                    | Refresh JWT token                  | No           |

---

## Authentication

This service uses JWT authentication via [djangorestframework-simplejwt](https://github.com/jazzband/djangorestframework-simplejwt).

- **Obtain a token:**
  - `POST /api/token/` with username and password.
- **Refresh a token:**
  - `POST /api/token/refresh/` with refresh token.

Include the access token in the `Authorization` header as:
```
Authorization: Bearer <your-access-token>
```

---

## API Documentation

Interactive and static API documentation is available:

- **Swagger UI (drf-yasg):** [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **Redoc (drf-yasg):** [http://localhost:8000/redoc/](http://localhost:8000/redoc/)
- **OpenAPI schema (drf-spectacular):** [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/)
- **Swagger UI (drf-spectacular):** [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/)
- **Redoc (drf-spectacular):** [http://localhost:8000/api/schema/redoc/](http://localhost:8000/api/schema/redoc/)

---

## Health Check

- **Endpoint:** `/health/`
- **Response Example:**
  ```json
  {
    "status": "healthy",
    "service": "analytics-service",
    "version": "1.0.0"
  }
  ```

---

## Static Files

- Static files are served from `/static/`.
- Collected in the `staticfiles/` directory.
- To collect static files for production:
  ```bash
  python manage.py collectstatic
  ```

---

## Testing

To run the test suite:
```bash
python manage.py test
```

- Tests are located in the `analytics_service/tests/` directory.
- Ensure all tests pass before deploying or pushing changes.

---

## Deployment

- Use a production-ready WSGI server (e.g., Gunicorn, uWSGI) behind a reverse proxy (e.g., Nginx).
- Set `DEBUG=False` and configure allowed hosts and database settings for production.
- Use environment variables for all sensitive configuration.
- Collect static files before deployment.
- Consider using Docker for containerized deployments.

---

## Contribution Guidelines

1. Fork the repository and create your branch from `main`.
2. Write clear, concise commit messages.
3. Add tests for new features and ensure existing tests pass.
4. Update documentation as needed.
5. Submit a pull request for review.

---

## License

This project is licensed under the [MIT License](../LICENSE) (or your license).

---

## Contact

For questions, issues, or support, please contact the development team or open an issue in the repository. 