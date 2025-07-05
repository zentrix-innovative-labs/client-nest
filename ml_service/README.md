# ML Service Microservice

This microservice provides recommendation and churn prediction APIs for the client-nest platform. It is designed to be production-ready, modular, and easy to integrate with the Django backend.

## Features
- Collaborative Filtering Recommender
- Content-Based Recommender
- Hybrid Recommender
- Churn Prediction
- FastAPI-powered REST API
- Dockerized for deployment

## Endpoints
- `POST /recommend` — Get recommendations for a user. Supports algorithm selection: `collaborative`, `content`, `hybrid`.
- `POST /churn-predict` — Predict churn risk for a user.

## Example Request: /recommend
```json
{
  "user_id": 123,
  "context": {"recent_views": [1,2,3]},
  "algorithm": "hybrid"
}
```

## Example Response: /recommend
```json
{
  "recommendations": [101, 102, 103],
  "algorithm": "hybrid"
}
```

## Example Request: /churn-predict
```json
{
  "user_id": 123,
  "features": {"activity": 0.5, "purchases": 2}
}
```

## Example Response: /churn-predict
```json
{
  "churn_risk": 0.23
}
```

## Running Locally
```bash
docker build -t ml_service .
docker run -p 8001:8000 ml_service
```

## Integration
- The Django backend should call the ML service via HTTP (e.g., using `requests` or `httpx`).
- See the OpenAPI docs at `/docs` when the service is running.

---

For more details, see `main.py`, `recommender.py`, and `churn.py` in this directory. 