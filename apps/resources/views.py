"""
Views for resources library (PDFs, audio, videos, etc.).
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.http import FileResponse, Http404
from django.contrib import messages
from .models import Resource, ResourceCategory


class ResourceListView(ListView):
    """
    Display a list of all resources, with filtering by category and type.
    """
    model = Resource
    template_name = 'resources/list.html'
    context_object_name = 'resources'
    paginate_by = 12

    def get_queryset(self):
        """
        Get all resources, optionally filtered by category or type.
        """
        queryset = Resource.objects.all()
        
        # Filter by category if provided
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by type if provided
        resource_type = self.request.GET.get('type')
        if resource_type:
            queryset = queryset.filter(type=resource_type)
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                description__icontains=search
            )
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ResourceCategory.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['current_type'] = self.request.GET.get('type')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ResourceDetailView(DetailView):
    """
    Display a single resource in detail.
    """
    model = Resource
    template_name = 'resources/detail.html'
    context_object_name = 'resource'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related resources (same category)
        context['related_resources'] = Resource.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        return context


def download_resource(request, slug):
    """
    Handle resource downloads and increment download count.
    """
    resource = get_object_or_404(Resource, slug=slug)
    
    if resource.file:
        # Increment download count
        resource.download_count += 1
        resource.save(update_fields=['download_count'])
        
        # Return the file for download
        return FileResponse(
            resource.file.open(),
            as_attachment=True,
            filename=resource.file.name.split('/')[-1]
        )
    else:
        raise Http404("This resource has no file attached.")
