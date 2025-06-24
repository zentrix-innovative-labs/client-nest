from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Custom admin class to set ordering
class CustomUserAdmin(UserAdmin):
    ordering = ['id']
    # Optionally, customize list_display, search_fields, etc.

# Set admin_order to 2 so it appears below Groups
admin.site.register(User, CustomUserAdmin)
User._meta.admin_order = 2
