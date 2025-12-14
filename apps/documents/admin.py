from django.contrib import admin

from .models import PRDDocument


@admin.register(PRDDocument)
class PRDDocumentAdmin(admin.ModelAdmin):
    """Admin configuration for PRDDocument model."""

    list_display = [
        'problem',
        'version',
        'status',
        'is_approved',
        'word_count',
        'created_by',
        'created_at',
    ]
    list_filter = [
        'status',
        'is_approved',
        'created_at',
        'problem__organization',
    ]
    search_fields = [
        'problem__title',
        'content',
        'summary',
    ]
    readonly_fields = [
        'id',
        'version',
        'word_count',
        'created_at',
        'updated_at',
        'approved_at',
    ]
    raw_id_fields = [
        'problem',
        'created_by',
        'approved_by',
        'parent_version',
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Identificacao', {
            'fields': ('id', 'problem', 'version', 'parent_version')
        }),
        ('Conteudo', {
            'fields': ('content', 'summary', 'word_count')
        }),
        ('Status', {
            'fields': ('status', 'is_approved', 'change_notes')
        }),
        ('Aprovacao', {
            'fields': ('approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
