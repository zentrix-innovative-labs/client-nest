"""
Mixin classes for common viewset functionality.
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
        Instead, implement the _get_actual_queryset() method to provide the actual queryset logic.
        The swagger_fake_view guard is automatically applied here.
        """
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.model.objects.none()
        return self._get_actual_queryset()
    
    def _get_actual_queryset(self):
        """
        Override this method to provide the actual queryset logic.
        This method will only be called when not in swagger_fake_view mode.
        """
        raise NotImplementedError("Subclasses must implement _get_actual_queryset()") 