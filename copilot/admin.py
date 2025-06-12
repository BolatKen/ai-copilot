from django.contrib import admin
from .models import Content, Tag, ModerationResult

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'file_type', 'safety_status', 'uploaded_at']
    list_filter = ['file_type', 'safety_status', 'uploaded_at']
    search_fields = ['file']
    readonly_fields = ['uploaded_at']

@admin.register(ModerationResult)
class ModerationResultAdmin(admin.ModelAdmin):
    list_display = ['content', 'analyzed_at', 'get_safety_status', 'is_checked_by_moderator', 'moderator_tags']
    list_filter = ['analyzed_at', 'content__safety_status']
    filter_horizontal = ['detected_tags']
    readonly_fields = ['analyzed_at']
    search_fields = ('moderator_tags',)
    
    def get_safety_status(self, obj):
        return obj.content.safety_status
    get_safety_status.short_description = 'Safety Status'

