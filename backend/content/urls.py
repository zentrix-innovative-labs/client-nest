from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'comment-likes', views.CommentLikeViewSet, basename='comment-like')
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
] 