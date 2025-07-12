# microservices/ai-service/content_generation/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import GeneratedContent, ContentTemplate, AIUsageLog
from .serializers import (
    ContentGenerationRequestSerializer,
    ContentGenerationResponseSerializer,
    GeneratedContentSerializer,
    ContentTemplateSerializer,
    AIUsageLogSerializer
)
from .logic import ContentGenerator
from common.deepseek_client import DeepSeekClient
import logging

logger = logging.getLogger(__name__)

class ContentGenerationTestAPIView(APIView):
    """
    Test API endpoint for generating social media content using AI (no authentication required).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContentGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Initialize AI client and content generator
            client = DeepSeekClient()
            generator = ContentGenerator(client)
            
            # Generate content
            result = generator.generate_post(
                topic=serializer.validated_data['topic'],
                platform=serializer.validated_data['platform'],
                user=None,  # No user for test endpoint
                tone=serializer.validated_data['tone'],
                content_type=serializer.validated_data.get('content_type', 'post'),
                additional_context=serializer.validated_data.get('additional_context')
            )
            
            if 'error' in result:
                return Response({'error': result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Validate response structure
            response_serializer = ContentGenerationResponseSerializer(data=result)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid response structure', 'details': response_serializer.errors},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return Response(
                {'error': 'An error occurred while generating content'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ContentGenerationAPIView(APIView):
    """
    API endpoint for generating social media content using AI.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContentGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Initialize AI client and content generator
            client = DeepSeekClient()
            generator = ContentGenerator(client)
            
            # Generate content
            result = generator.generate_post(
                topic=serializer.validated_data['topic'],
                platform=serializer.validated_data['platform'],
                user=request.user,
                tone=serializer.validated_data['tone'],
                content_type=serializer.validated_data.get('content_type', 'post'),
                additional_context=serializer.validated_data.get('additional_context')
            )
            
            if 'error' in result:
                return Response({'error': result['error']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Save generated content to database
            generated_content = GeneratedContent.objects.create(
                user=request.user,
                topic=serializer.validated_data['topic'],
                platform=serializer.validated_data['platform'],
                tone=serializer.validated_data['tone'],
                content=result['content'],
                hashtags=result['hashtags'],
                call_to_action=result.get('call_to_action', ''),
                suggestions=result.get('suggestions', []),
                variations=result.get('variations', []),
                quality_score=result['quality_score'],
                safety_check=result['safety_check'],
                readability_score=result['readability_score'],
                engagement_prediction=result['engagement_prediction'],
                optimal_posting_time_suggestion=result['optimal_posting_time_suggestion']
            )
            
            # Validate response structure
            response_serializer = ContentGenerationResponseSerializer(data=result)
            if response_serializer.is_valid():
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Invalid response structure', 'details': response_serializer.errors},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return Response(
                {'error': 'An error occurred while generating content'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GeneratedContentListView(APIView):
    """
    API endpoint for listing user's generated content.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = GeneratedContent.objects.filter(user=request.user)
        serializer = GeneratedContentSerializer(content, many=True)
        return Response(serializer.data)

class GeneratedContentDetailView(APIView):
    """
    API endpoint for retrieving specific generated content.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, content_id):
        content = get_object_or_404(GeneratedContent, id=content_id, user=request.user)
        serializer = GeneratedContentSerializer(content)
        return Response(serializer.data)

class ContentTemplateListView(APIView):
    """
    API endpoint for listing content templates.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        templates = ContentTemplate.objects.filter(is_active=True)
        serializer = ContentTemplateSerializer(templates, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContentTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AIUsageLogListView(APIView):
    """
    API endpoint for listing AI usage logs.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AIUsageLog.objects.filter(user=request.user)
        serializer = AIUsageLogSerializer(logs, many=True)
        return Response(serializer.data) 