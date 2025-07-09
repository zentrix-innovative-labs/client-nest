import requests
import json
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import UserInteraction, Recommendation, ChurnPrediction
from users.models import User, UserProfile
from social_media.models import PostAnalytics, SocialAccount
from ai_integration.models import AIUsageLog

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Service for handling recommendation system operations
    """
    
    def __init__(self, ml_service_url: str = None):
        self.ml_service_url = ml_service_url or getattr(settings, 'ML_SERVICE_URL', 'http://localhost:8001')
    
    def extract_user_interactions(self, user_id: int, days_back: int = 30) -> Dict:
        """
        Extract user interactions for ML service
        """
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        # Get user interactions
        interactions = UserInteraction.objects.filter(
            user_id=user_id,
            created_at__gte=cutoff_date
        ).values('interaction_type', 'content_id', 'content_type')
        
        # Get social media analytics
        social_analytics = PostAnalytics.objects.filter(
            social_account__user_id=user_id,
            created_at__gte=cutoff_date
        ).aggregate(
            total_likes=Count('likes'),
            total_comments=Count('comments'),
            total_shares=Count('shares'),
            avg_engagement=Avg('engagement_rate')
        )
        
        # Get AI usage
        ai_usage = AIUsageLog.objects.filter(
            user_id=user_id,
            created_at__gte=cutoff_date
        ).aggregate(
            total_requests=Count('id'),
            total_cost=Avg('cost')
        )
        
        return {
            'user_id': user_id,
            'interactions': list(interactions),
            'social_analytics': social_analytics,
            'ai_usage': ai_usage,
            'extraction_date': timezone.now().isoformat()
        }
    
    def get_user_features(self, user_id: int) -> Dict:
        """
        Extract user features for content-based recommendations
        """
        try:
            user = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(user=user)
            
            # Get user preferences
            preferences = profile.preferences if hasattr(profile, 'preferences') else {}
            
            # Get social media accounts
            social_accounts = SocialAccount.objects.filter(user=user).values_list('platform', flat=True)
            
            # Get recent interaction patterns
            recent_interactions = UserInteraction.objects.filter(
                user_id=user_id,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).values('interaction_type').annotate(count=Count('id'))
            
            interaction_patterns = {item['interaction_type']: item['count'] for item in recent_interactions}
            
            return {
                'user_id': user_id,
                'preferences': preferences,
                'social_platforms': list(social_accounts),
                'interaction_patterns': interaction_patterns,
                'join_date': user.created_at.isoformat(),
                'is_active': user.is_active
            }
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            logger.error(f"User or profile not found for user_id: {user_id}")
            return {}
    
    def call_ml_service(self, endpoint: str, data: Dict) -> Optional[Dict]:
        """
        Make HTTP request to ML microservice
        """
        try:
            url = f"{self.ml_service_url}/{endpoint}"
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling ML service {endpoint}: {str(e)}")
            return None
    
    def get_recommendations(self, user_id: int, algorithm: str = 'hybrid', top_k: int = 10) -> List[Dict]:
        """
        Get recommendations for a user
        """
        # Extract user data
        user_features = self.get_user_features(user_id)
        user_interactions = self.extract_user_interactions(user_id)
        
        # Prepare request for ML service
        request_data = {
            'user_id': user_id,
            'context': user_interactions,
            'algorithm': algorithm,
            'top_k': top_k
        }
        
        # Call ML service
        response = self.call_ml_service('recommend', request_data)
        
        if response and 'recommendations' in response:
            # Store recommendations in database
            recommendations = []
            for i, content_id in enumerate(response['recommendations']):
                score = 1.0 - (i * 0.1)  # Simple scoring based on position
                rec, created = Recommendation.objects.get_or_create(
                    user_id=user_id,
                    content_id=content_id,
                    algorithm=algorithm,
                    defaults={'score': score, 'content_type': 'post'}
                )
                recommendations.append({
                    'content_id': content_id,
                    'score': rec.score,
                    'algorithm': algorithm
                })
            
            return recommendations
        
        return []
    
    def predict_churn(self, user_id: int) -> Optional[float]:
        """
        Predict churn risk for a user
        """
        # Extract user features for churn prediction
        user_features = self.get_user_features(user_id)
        user_interactions = self.extract_user_interactions(user_id)
        
        # Calculate engagement features
        recent_interactions = UserInteraction.objects.filter(
            user_id=user_id,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Prepare request for ML service
        request_data = {
            'user_id': user_id,
            'features': {
                'recent_interactions': recent_interactions,
                'total_interactions': user_interactions.get('interactions', []),
                'social_activity': user_features.get('social_platforms', []),
                'ai_usage': user_interactions.get('ai_usage', {})
            }
        }
        
        # Call ML service
        response = self.call_ml_service('churn-predict', request_data)
        
        if response and 'churn_risk' in response:
            # Store prediction in database
            ChurnPrediction.objects.create(
                user_id=user_id,
                churn_risk=response['churn_risk'],
                features=request_data['features']
            )
            
            return response['churn_risk']
        
        return None
    
    def log_interaction(self, user_id: int, interaction_type: str, content_id: str, 
                       content_type: str = 'post', platform: str = '', metadata: Dict = None):
        """
        Log a user interaction for recommendation system
        """
        UserInteraction.objects.create(
            user_id=user_id,
            interaction_type=interaction_type,
            content_id=content_id,
            content_type=content_type,
            platform=platform,
            metadata=metadata or {}
        )
    
    def update_recommendation_feedback(self, user_id: int, content_id: str, 
                                     is_clicked: bool = False, is_dismissed: bool = False):
        """
        Update recommendation feedback for model improvement
        """
        try:
            recommendation = Recommendation.objects.get(
                user_id=user_id,
                content_id=content_id
            )
            if is_clicked:
                recommendation.is_clicked = True
            if is_dismissed:
                recommendation.is_dismissed = True
            recommendation.save()
        except Recommendation.DoesNotExist:
            logger.warning(f"Recommendation not found for user {user_id} and content {content_id}") 