from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Content, Tag, ModerationResult


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_count')
    search_fields = ('name',)
    ordering = ('name',)
    
    def content_count(self, obj):
        return obj.moderationresult_set.count()
    content_count.short_description = 'Количество контента'


class ModerationResultInline(admin.StackedInline):
    model = ModerationResult
    extra = 0
    readonly_fields = ('analyzed_at', 'ai_analysis_raw')
    fields = (
        'analyzed_at', 
        'detected_tags', 
        'ai_analysis_raw',
        'is_checked_by_moderator',
        'moderator_tags',
        'moderator_verdict'
    )


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'file_name', 
        'file_type', 
        'safety_status', 
        'uploaded_at',
        'is_moderated',
        'preview_link'
    )
    list_filter = ('file_type', 'safety_status', 'uploaded_at')
    search_fields = ('file',)
    readonly_fields = ('uploaded_at',)
    inlines = [ModerationResultInline]
    
    def file_name(self, obj):
        return obj.file.name.split('/')[-1]
    file_name.short_description = 'Имя файла'
    
    def is_moderated(self, obj):
        try:
            return obj.moderation_result.is_checked_by_moderator
        except:
            return False
    is_moderated.boolean = True
    is_moderated.short_description = 'Проверено модератором'
    
    def preview_link(self, obj):
        if obj.file_type == 'image':
            return format_html(
                '<a href="{}" target="_blank">Просмотр</a>',
                obj.file.url
            )
        return '-'
    preview_link.short_description = 'Предпросмотр'


@admin.register(ModerationResult)
class ModerationResultAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'content_file',
        'content_safety_status',
        'is_checked_by_moderator',
        'analyzed_at',
        'tags_list'
    )
    list_filter = (
        'is_checked_by_moderator', 
        'analyzed_at',
        'content__safety_status'
    )
    search_fields = ('content__file', 'moderator_tags', 'moderator_verdict')
    readonly_fields = ('analyzed_at', 'ai_analysis_raw')
    filter_horizontal = ('detected_tags',)
    
    def content_file(self, obj):
        return obj.content.file.name.split('/')[-1]
    content_file.short_description = 'Файл'
    
    def content_safety_status(self, obj):
        return obj.content.get_safety_status_display()
    content_safety_status.short_description = 'Статус безопасности'
    
    def tags_list(self, obj):
        return ', '.join([tag.name for tag in obj.detected_tags.all()])
    tags_list.short_description = 'Обнаруженные теги'


# Настройка интерфейса админ-панели
admin.site.site_header = 'AI Copilot Администрирование'
admin.site.site_title = 'AI Copilot Admin'
admin.site.index_title = 'Добро пожаловать в панель управления AI Copilot'

