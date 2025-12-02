from django.contrib import admin
from .models import ResourceCategory, Resource


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing resource categories.
    """
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """
    Admin interface for managing resources (PDFs, audio, videos, etc.).
    """
    list_display = ['title', 'category', 'type', 'is_featured', 'download_count', 'created_at']
    list_filter = ['type', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['download_count', 'created_at', 'updated_at']
