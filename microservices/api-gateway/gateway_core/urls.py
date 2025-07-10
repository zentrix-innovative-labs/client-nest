from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'services', views.ServiceRegistryViewSet, basename='service-registry')
router.register(r'routes', views.RouteConfigurationViewSet, basename='route-configuration')
router.register(r'logs', views.RequestLogViewSet, basename='request-log')
router.register(r'metrics', views.ServiceMetricsViewSet, basename='service-metrics')
router.register(r'circuit-breakers', views.CircuitBreakerStateViewSet, basename='circuit-breaker')
router.register(r'rate-limits', views.RateLimitRuleViewSet, basename='rate-limit')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]