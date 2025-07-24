from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from recommender import CollaborativeRecommender, ContentBasedRecommender, HybridRecommender
from churn import ChurnPredictor
import numpy as np
from typing import Dict, List, Optional, Any

app = FastAPI(title="ML Recommendation & Churn Service")

# Initialize recommenders with better default data
# In production, this would be loaded from database or file
user_item_matrix = np.array([
    [5, 0, 3, 0, 2, 1, 0, 4],
    [4, 0, 0, 1, 1, 0, 2, 0],
    [1, 1, 0, 5, 0, 3, 0, 1],
    [0, 0, 4, 4, 5, 0, 1, 2],
    [2, 3, 1, 0, 0, 4, 3, 0],
    [0, 2, 0, 2, 3, 1, 0, 5],
])

# More diverse item features for content-based filtering
item_features = np.array([
    [1, 0, 1, 0, 1],  # Technology
    [0, 1, 0, 1, 0],  # Lifestyle
    [1, 1, 0, 0, 1],  # Mixed
    [0, 0, 1, 1, 0],  # Business
    [1, 0, 0, 1, 1],  # Entertainment
    [0, 1, 1, 0, 0],  # Health
    [1, 0, 1, 1, 0],  # News
    [0, 1, 0, 0, 1],  # Sports
])

# Calculate user profiles based on their interactions
user_profiles = []
for i in range(user_item_matrix.shape[0]):
    user_interactions = user_item_matrix[i]
    interacted_items = np.where(user_interactions > 0)[0]
    if len(interacted_items) > 0:
        # Weighted average of interacted item features
        weights = user_interactions[interacted_items]
        profile = np.average(item_features[interacted_items], weights=weights, axis=0)
    else:
        profile = np.zeros(item_features.shape[1])
    user_profiles.append(profile)

collab = CollaborativeRecommender(user_item_matrix)
content = ContentBasedRecommender(item_features)
hybrid = HybridRecommender(collab, content)

churn_predictor = ChurnPredictor()
# Train churn predictor with more realistic data
X = np.array([
    [10, 5, 0.8],   # High activity, high purchases, high engagement
    [2, 1, 0.2],    # Low activity, low purchases, low engagement
    [8, 3, 0.6],    # Medium-high activity
    [1, 0, 0.1],    # Very low activity (likely to churn)
    [15, 8, 0.9],   # Very high activity
    [3, 2, 0.3],    # Low-medium activity
    [12, 6, 0.7],   # High activity
    [0, 0, 0.0],    # No activity (high churn risk)
    [6, 4, 0.5],    # Medium activity
    [4, 1, 0.4],    # Medium-low activity
])
y = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])  # 1 = churned, 0 = retained
churn_predictor.fit(X, y)

class RecommendRequest(BaseModel):
    user_id: int
    context: Dict[str, Any] = {}
    algorithm: str = "hybrid"
    top_k: int = 5

class RecommendResponse(BaseModel):
    recommendations: List[int]
    algorithm: str
    scores: Optional[List[float]] = None

class ChurnRequest(BaseModel):
    user_id: int
    features: Dict[str, Any]

class ChurnResponse(BaseModel):
    churn_risk: float
    risk_level: str
    confidence: float

@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    if req.user_id >= len(user_item_matrix):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Process context data if provided
    if req.context:
        # Update user profile based on recent interactions
        recent_interactions = req.context.get('interactions', [])
        if recent_interactions:
            # Update user profile with recent activity
            pass
    
    if req.algorithm == "collaborative":
        recs = collab.recommend(req.user_id, req.top_k)
        scores = [1.0 - (i * 0.1) for i in range(len(recs))]
    elif req.algorithm == "content":
        user_profile = user_profiles[req.user_id]
        recs = content.recommend(user_profile, req.top_k)
        scores = [1.0 - (i * 0.1) for i in range(len(recs))]
    elif req.algorithm == "hybrid":
        user_profile = user_profiles[req.user_id]
        recs = hybrid.recommend(req.user_id, user_profile, req.top_k)
        scores = [1.0 - (i * 0.1) for i in range(len(recs))]
    else:
        raise HTTPException(status_code=400, detail="Unknown algorithm")
    
    return RecommendResponse(
        recommendations=recs,
        algorithm=req.algorithm,
        scores=scores
    )

@app.post("/churn-predict", response_model=ChurnResponse)
def churn_predict(req: ChurnRequest):
    # Extract features from request
    features = req.features
    
    # Convert features to numerical array
    feature_vector = []
    
    # Recent interactions (normalized)
    recent_interactions = features.get('recent_interactions', 0)
    feature_vector.append(min(recent_interactions / 10.0, 1.0))  # Normalize to 0-1
    
    # Social activity (number of platforms)
    social_activity = len(features.get('social_activity', []))
    feature_vector.append(min(social_activity / 5.0, 1.0))  # Normalize to 0-1
    
    # AI usage (engagement level)
    ai_usage = features.get('ai_usage', {})
    total_requests = ai_usage.get('total_requests', 0)
    feature_vector.append(min(total_requests / 20.0, 1.0))  # Normalize to 0-1
    
    # Ensure we have exactly 3 features
    while len(feature_vector) < 3:
        feature_vector.append(0.0)
    feature_vector = feature_vector[:3]
    
    risk = churn_predictor.predict(feature_vector)
    
    # Determine risk level
    if risk < 0.3:
        risk_level = "low"
        confidence = 0.8
    elif risk < 0.7:
        risk_level = "medium"
        confidence = 0.6
    else:
        risk_level = "high"
        confidence = 0.9
    
    return ChurnResponse(
        churn_risk=risk,
        risk_level=risk_level,
        confidence=confidence
    )

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ML Recommendation Service"}

@app.get("/")
def root():
    return {
        "message": "ML Recommendation & Churn Service",
        "endpoints": {
            "recommend": "/recommend",
            "churn-predict": "/churn-predict",
            "health": "/health",
            "docs": "/docs"
        }
    } 