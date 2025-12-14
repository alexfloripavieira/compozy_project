"""
Admin configuration for the Chat app.

This module registers the ChatMessage model with Django admin
and configures its display and editing options.
"""

from django.contrib import admin
from django.utils.html import format_html

from apps.chat.models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin configuration for ChatMessage model."""

    list_display = [
        'id_short',
        'problem_title',
        'sender_badge',
        'message_type_badge',
        'content_preview',
        'is_read',
        'created_at',
    ]
    list_filter = [
        'sender_type',
        'message_type',
        'agent_name',
        'is_read',
        'created_at',
    ]
    search_fields = [
        'content',
        'problem__title',
        'sender_user__username',
        'agent_name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 50

    fieldsets = (
        ('Informacoes Basicas', {
            'fields': ('id', 'problem', 'content')
        }),
        ('Remetente', {
            'fields': ('sender_type', 'sender_user', 'agent_name')
        }),
        ('Tipo e Status', {
            'fields': ('message_type', 'is_read')
        }),
        ('Metadados', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def id_short(self, obj):
        """Display shortened UUID."""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'

    def problem_title(self, obj):
        """Display problem title."""
        return obj.problem.title[:30] + '...' if len(obj.problem.title) > 30 else obj.problem.title
    problem_title.short_description = 'Problema'
    problem_title.admin_order_field = 'problem__title'

    def content_preview(self, obj):
        """Display content preview."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Conteudo'

    def sender_badge(self, obj):
        """Display sender as a colored badge."""
        if obj.sender_type == 'user':
            name = obj.sender_user.username if obj.sender_user else 'Usuario'
            color = '#3b82f6'  # blue
        else:
            name = dict(ChatMessage.AGENT_NAME_CHOICES).get(obj.agent_name, obj.agent_name)
            color = '#8b5cf6'  # purple
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            name
        )
    sender_badge.short_description = 'Remetente'

    def message_type_badge(self, obj):
        """Display message type as a colored badge."""
        colors = {
            'question': '#f59e0b',  # amber
            'answer': '#10b981',  # green
            'info': '#3b82f6',  # blue
            'error': '#ef4444',  # red
            'system': '#6b7280',  # gray
        }
        color = colors.get(obj.message_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_message_type_display()
        )
    message_type_badge.short_description = 'Tipo'
    message_type_badge.admin_order_field = 'message_type'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'problem', 'sender_user'
        )

    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description='Marcar como lida')
    def mark_as_read(self, request, queryset):
        """Mark selected messages as read."""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} mensagem(ns) marcada(s) como lida(s).')

    @admin.action(description='Marcar como nao lida')
    def mark_as_unread(self, request, queryset):
        """Mark selected messages as unread."""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} mensagem(ns) marcada(s) como nao lida(s).')
