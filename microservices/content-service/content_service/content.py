# empty

from django.db import models

class Content(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

        from rest_framework import serializers
from .models import Content

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'

        from rest_framework import generics
from .models import Content
from .serializers import ContentSerializer

class ContentListCreateView(generics.ListCreateAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

class ContentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

    from django.urls import path
from .views import ContentListCreateView, ContentDetailView

urlpatterns = [
    path('', ContentListCreateView.as_view(), name='content-list-create'),
    path('<int:pk>/', ContentDetailView.as_view(), name='content-detail'),
]

from django.contrib import admin
from .models import Content

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')

    from django.test import TestCase
from .models import Content

class ContentModelTest(TestCase):
    def test_create_content(self):
        content = Content.objects.create(title="Test", body="Test body")
        self.assertEqual(content.title, "Test")
        self.assertEqual(content.body, "Test body")

        # empty