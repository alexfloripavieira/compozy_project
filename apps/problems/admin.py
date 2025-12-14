"""
Admin configuration for the Problems app.

This module registers the Problem model with Django admin
and configures its display and editing options.
"""

from django.contrib import admin
from django.utils.html import format_html

from apps.problems.models import Problem


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    """Admin configuration for Problem model."""

    list_display = [
        'title',
        'organization',
        'status_badge',
        'priority_badge',
        'created_by',
        'created_at',
        'updated_at',
    ]
    list_filter = [
        'status',
        'priority',
        'organization',
        'created_at',
    ]
    search_fields = [
        'title',
        'description',
        'organization__name',
        'created_by__username',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'workflow_id',
    ]
    filter_horizontal = ['repositories']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Informacoes Basicas', {
            'fields': ('id', 'title', 'description', 'organization', 'created_by')
        }),
        ('Status e Prioridade', {
            'fields': ('status', 'priority', 'error_message')
        }),
        ('Repositorios', {
            'fields': ('repositories',)
        }),
        ('Workflow', {
            'fields': ('workflow_id',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'draft': '#6b7280',  # gray
            'analyzing': '#3b82f6',  # blue
            'prd_generation': '#3b82f6',  # blue
            'prd_review': '#f59e0b',  # amber
            'spec_generation': '#3b82f6',  # blue
            'spec_review': '#f59e0b',  # amber
            'task_creation': '#3b82f6',  # blue
            'task_selection': '#f59e0b',  # amber
            'executing': '#8b5cf6',  # purple
            'testing': '#8b5cf6',  # purple
            'completed': '#10b981',  # green
            'failed': '#ef4444',  # red
            'cancelled': '#6b7280',  # gray
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def priority_badge(self, obj):
        """Display priority as a colored badge."""
        colors = {
            'low': '#6b7280',  # gray
            'medium': '#3b82f6',  # blue
            'high': '#f59e0b',  # amber
            'critical': '#ef4444',  # red
        }
        color = colors.get(obj.priority, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Prioridade'
    priority_badge.admin_order_field = 'priority'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'organization', 'created_by'
        )
