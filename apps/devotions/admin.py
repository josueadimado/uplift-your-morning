from django.contrib import admin
from .models import DevotionSeries, Devotion


@admin.register(DevotionSeries)
class DevotionSeriesAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'start_date', 'end_date', 'created_at']
    list_filter = ['is_active', 'start_date']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Media', {
            'fields': ('banner_image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Devotion)
class DevotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'theme', 'series', 'publish_date', 'is_published', 'featured', 'view_count']
    list_filter = ['is_published', 'featured', 'publish_date', 'series', 'theme']
    search_fields = ['title', 'topic', 'theme', 'scripture_reference', 'body']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    date_hierarchy = 'publish_date'
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'series', 'theme', 'topic', 'publish_date', 'is_published', 'featured')
        }),
        ('Scripture', {
            'fields': ('scripture_reference', 'passage_text')
        }),
        ('Content', {
            'fields': ('body', 'quote', 'reflection', 'prayer', 'action_point')
        }),
        ('Media', {
            'fields': ('image', 'audio_file', 'pdf_file')
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at')
        }),
    )
