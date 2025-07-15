from django.urls import path
from .views import generate_content_endpoint
 
urlpatterns = [
    path('generate-content/', generate_content_endpoint, name='generate_content'),
] 