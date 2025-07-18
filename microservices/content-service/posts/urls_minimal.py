from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_minimal import PostViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    path('api/v1/', include(router.urls)),
] 