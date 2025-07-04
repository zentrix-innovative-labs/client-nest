"""
Custom mixin classes for common viewset functionality in the ClientNest project.

This module contains mixins designed specifically for this Django REST Framework project
to handle common patterns like Swagger schema generation and queryset management.

Created for ClientNest project - not derived from external sources.
"""

class SwaggerFakeViewMixin:
    """
    Mixin to handle swagger_fake_view detection in get_queryset methods.
    
    This prevents schema generation errors when drf-yasg tries to generate
    OpenAPI documentation without a real request context.
    
    IMPORTANT: This mixin must be placed BEFORE ModelViewSet in the class hierarchy.
    Example: class MyViewSet(SwaggerFakeViewMixin, viewsets.ModelViewSet):
    
    This ensures that the mixin's get_queryset method takes precedence over
    ModelViewSet's get_queryset method due to Python's method resolution order (MRO).
    If placed after ModelViewSet, the mixin's get_queryset would never be called.
    """
    
    def get_queryset(self):
        """
        Do not override this method in subclasses.
        Instead, implement the get_actual_queryset() method to provide the actual queryset logic.
        The swagger_fake_view guard is automatically applied here.
        """
        if getattr(self, 'swagger_fake_view', False):
            if hasattr(self, 'queryset') and self.queryset is not None:
                return self.queryset.model.objects.none()
            # Fallback: try to use self.serializer_class.Meta.model if available
            serializer_class = getattr(self, 'serializer_class', None)
            if serializer_class and hasattr(serializer_class, 'Meta') and hasattr(serializer_class.Meta, 'model'):
                return serializer_class.Meta.model.objects.none()
            # Otherwise, return []
            return []
        return self.get_actual_queryset()
    
    def get_actual_queryset(self):
        """
        Override this method to provide the actual queryset logic.
        This method will only be called when not in swagger_fake_view mode.
        """
        raise NotImplementedError("Subclasses must implement get_actual_queryset()") 