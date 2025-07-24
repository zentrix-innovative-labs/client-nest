from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('recommendations/', views.RecommendationAPIView.as_view(), name='recommendations'),
    path('churn-prediction/', views.ChurnPredictionAPIView.as_view(), name='churn-prediction'),
    path('interactions/', views.UserInteractionAPIView.as_view(), name='interactions'),
    path('feedback/', views.RecommendationFeedbackAPIView.as_view(), name='feedback'),
    path('stats/', views.recommendation_stats, name='stats'),
] 