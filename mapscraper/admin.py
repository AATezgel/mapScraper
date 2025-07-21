from django.contrib import admin
from django.utils.html import format_html
from .models import MapData, ScrapingJob
from .supabase_service import supabase_service

@admin.register(MapData)
class MapDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'rating', 'category', 'supabase_status', 'created_at')
    list_filter = ('category', 'rating', 'created_at')
    search_fields = ('name', 'address', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')
    
    def supabase_status(self, obj):
        """Supabase bağlantı durumunu göster"""
        if supabase_service.is_connected():
            return format_html('<span style="color: green;">✓ Bağlı</span>')
        else:
            return format_html('<span style="color: red;">✗ Bağlı değil</span>')
    supabase_status.short_description = 'Supabase'

@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ('query', 'user', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('query', 'user__username')
    readonly_fields = ('created_at', 'completed_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')
