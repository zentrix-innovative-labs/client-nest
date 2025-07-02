from django.urls import path
from client_nest.ai_services.common.views import generate_content_endpoint

urlpatterns = [
    path('generate-content/', generate_content_endpoint, name='generate_content'),
] 