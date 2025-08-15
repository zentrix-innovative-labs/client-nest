from django.urls import path
from . import views

urlpatterns = [
    # Token validation endpoint (used internally by middleware)
    path('validate-token/', views.validate_token, name='validate-token'),
    
    # Authentication proxy endpoints
    path('login/', views.proxy_login, name='proxy-login'),
    path('register/', views.proxy_register, name='proxy-register'),
    path('refresh/', views.proxy_refresh_token, name='proxy-refresh'),
    path('logout/', views.logout, name='logout'),
    
    # User info endpoint
    path('user-info/', views.get_user_info, name='user-info'),
    
    # Health check
    path('health/', views.health_check, name='auth-health'),
]