"""
Admin configuration for the Tasks app.

This module registers the Task model with Django admin
and configures its display and editing options.
"""

from django.contrib import admin
from django.utils.html import format_html

from apps.tasks_app.models import Task, TaskExecution


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model."""

    list_display = [
        'title',
        'problem',
        'status_badge',
        'priority_badge',
        'order_index',
        'dependencies_count',
        'started_at',
        'completed_at',
    ]
    list_filter = [
        'status',
        'priority',
        'task_type',
        'problem__organization',
        'created_at',
    ]
    search_fields = [
        'title',
        'description',
        'spec',
        'problem__title',
        'problem__organization__name',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'started_at',
        'completed_at',
        'actual_hours',
        'duration_display',
    ]
    filter_horizontal = ['dependencies']
    date_hierarchy = 'created_at'
    ordering = ['problem', 'order_index']
    list_per_page = 25

    fieldsets = (
        ('Informacoes Basicas', {
            'fields': ('id', 'title', 'description', 'problem', 'tech_spec')
        }),
        ('Especificacao', {
            'fields': ('spec',),
            'classes': ('collapse',)
        }),
        ('Status e Prioridade', {
            'fields': ('status', 'priority', 'task_type', 'order_index')
        }),
        ('Dependencias', {
            'fields': ('dependencies',),
            'classes': ('collapse',)
        }),
        ('Execucao', {
            'fields': (
                'started_at', 'completed_at', 'duration_display',
                'estimated_hours', 'actual_hours', 'error_message'
            )
        }),
        ('Git', {
            'fields': ('branch_name', 'commit_sha'),
            'classes': ('collapse',)
        }),
        ('Dados de Implementacao', {
            'fields': ('implementation', 'test_results'),
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
            'pending': '#6b7280',  # gray
            'selected': '#3b82f6',  # blue
            'in_progress': '#8b5cf6',  # purple
            'testing': '#f59e0b',  # amber
            'completed': '#10b981',  # green
            'failed': '#ef4444',  # red
            'skipped': '#6b7280',  # gray
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

    def dependencies_count(self, obj):
        """Display count of dependencies."""
        count = obj.dependencies.count()
        if count == 0:
            return '-'
        return format_html(
            '<span style="background-color: #e5e7eb; padding: 2px 6px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            count
        )
    dependencies_count.short_description = 'Deps'

    def duration_display(self, obj):
        """Display duration in human-readable format."""
        seconds = obj.duration_seconds
        if seconds is None:
            return '-'

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            return f'{hours}h {minutes}m'
        return f'{minutes}m'
    duration_display.short_description = 'Duracao'

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related."""
        return super().get_queryset(request).select_related(
            'problem', 'problem__organization', 'tech_spec'
        ).prefetch_related('dependencies')

    actions = ['mark_as_selected', 'mark_as_pending', 'reset_tasks']

    @admin.action(description='Marcar como selecionado')
    def mark_as_selected(self, request, queryset):
        """Mark selected tasks as 'selected'."""
        updated = queryset.filter(status='pending').update(status='selected')
        self.message_user(request, f'{updated} tarefa(s) marcada(s) como selecionada(s).')

    @admin.action(description='Marcar como pendente')
    def mark_as_pending(self, request, queryset):
        """Mark selected tasks as 'pending'."""
        updated = queryset.exclude(
            status__in=['in_progress', 'testing']
        ).update(status='pending')
        self.message_user(request, f'{updated} tarefa(s) marcada(s) como pendente(s).')

    @admin.action(description='Resetar tarefas')
    def reset_tasks(self, request, queryset):
        """Reset selected tasks to initial state."""
        count = 0
        for task in queryset:
            task.reset()
            count += 1
        self.message_user(request, f'{count} tarefa(s) resetada(s).')


class StatusFilter(admin.SimpleListFilter):
    """Custom filter for TaskExecution status with execution counts."""

    title = 'Status'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        """Return filter options with counts."""
        return [
            ('pending', 'Pendente'),
            ('running', 'Executando'),
            ('completed', 'Concluido'),
            ('failed', 'Falhou'),
            ('cancelled', 'Cancelado'),
            ('timeout', 'Tempo Esgotado'),
        ]

    def queryset(self, request, queryset):
        """Filter queryset by status."""
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class AgentTypeFilter(admin.SimpleListFilter):
    """Custom filter for agent type."""

    title = 'Tipo de Agente'
    parameter_name = 'agent_type'

    def lookups(self, request, model_admin):
        """Return filter options."""
        return TaskExecution.AGENT_TYPE_CHOICES

    def queryset(self, request, queryset):
        """Filter queryset by agent type."""
        if self.value():
            return queryset.filter(agent_type=self.value())
        return queryset


class ExecutionOutcomeFilter(admin.SimpleListFilter):
    """Filter executions by outcome (success/failure)."""

    title = 'Resultado'
    parameter_name = 'outcome'

    def lookups(self, request, model_admin):
        """Return filter options."""
        return [
            ('success', 'Sucesso'),
            ('failure', 'Falha'),
            ('in_progress', 'Em Andamento'),
        ]

    def queryset(self, request, queryset):
        """Filter queryset by outcome."""
        if self.value() == 'success':
            return queryset.filter(status='completed')
        elif self.value() == 'failure':
            return queryset.filter(status__in=['failed', 'cancelled', 'timeout'])
        elif self.value() == 'in_progress':
            return queryset.filter(status__in=['pending', 'running'])
        return queryset


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    """Admin configuration for TaskExecution model."""

    list_display = [
        'execution_summary',
        'task_link',
        'status_badge',
        'agent_type_badge',
        'attempt_number',
        'duration_display',
        'started_at',
        'completed_at',
    ]
    list_filter = [
        StatusFilter,
        AgentTypeFilter,
        ExecutionOutcomeFilter,
        'created_at',
        'started_at',
        'task__problem__organization',
    ]
    search_fields = [
        'task__title',
        'task__problem__title',
        'celery_task_id',
        'error_message',
        'logs',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'started_at',
        'completed_at',
        'duration_display',
        'attempt_number',
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_per_page = 25
    raw_id_fields = ['task']

    fieldsets = (
        ('Informacoes Basicas', {
            'fields': ('id', 'task', 'attempt_number', 'status', 'agent_type')
        }),
        ('Celery', {
            'fields': ('celery_task_id',),
            'classes': ('collapse',)
        }),
        ('Tempo de Execucao', {
            'fields': ('started_at', 'completed_at', 'duration_display')
        }),
        ('Logs e Saida', {
            'fields': ('logs', 'output'),
            'classes': ('collapse',)
        }),
        ('Erros', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Metricas', {
            'fields': ('metrics',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def execution_summary(self, obj):
        """Display a summary of the execution."""
        return f'Exec #{obj.attempt_number}'
    execution_summary.short_description = 'Execucao'

    def task_link(self, obj):
        """Display task as a clickable link."""
        from django.urls import reverse
        url = reverse('admin:tasks_app_task_change', args=[obj.task.pk])
        return format_html(
            '<a href="{}" title="{}">{}</a>',
            url,
            obj.task.title,
            obj.task.title[:50] + '...' if len(obj.task.title) > 50 else obj.task.title
        )
    task_link.short_description = 'Tarefa'

    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'pending': '#6b7280',  # gray
            'running': '#8b5cf6',  # purple
            'completed': '#10b981',  # green
            'failed': '#ef4444',  # red
            'cancelled': '#f59e0b',  # amber
            'timeout': '#dc2626',  # darker red
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

    def agent_type_badge(self, obj):
        """Display agent type as a badge."""
        colors = {
            'code_writer': '#3b82f6',  # blue
            'test_runner': '#10b981',  # green
            'business_analyst': '#8b5cf6',  # purple
            'tech_architect': '#f59e0b',  # amber
            'task_planner': '#ec4899',  # pink
            'unknown': '#6b7280',  # gray
        }
        color = colors.get(obj.agent_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_agent_type_display()
        )
    agent_type_badge.short_description = 'Agente'
    agent_type_badge.admin_order_field = 'agent_type'

    def duration_display(self, obj):
        """Display duration in human-readable format."""
        seconds = obj.duration_seconds
        if seconds is None:
            return '-'

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f'{hours}h {minutes}m'
        elif minutes > 0:
            return f'{minutes}m {secs}s'
        return f'{secs}s'
    duration_display.short_description = 'Duracao'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related(
            'task', 'task__problem', 'task__problem__organization'
        )

    actions = ['cancel_executions', 'mark_as_failed']

    @admin.action(description='Cancelar execucoes')
    def cancel_executions(self, request, queryset):
        """Cancel selected executions."""
        count = 0
        for execution in queryset.filter(status__in=['pending', 'running']):
            try:
                execution.cancel()
                count += 1
            except Exception:
                pass
        self.message_user(request, f'{count} execucao(oes) cancelada(s).')

    @admin.action(description='Marcar como falha')
    def mark_as_failed(self, request, queryset):
        """Mark selected executions as failed."""
        count = 0
        for execution in queryset.exclude(status__in=['completed', 'failed', 'cancelled', 'timeout']):
            try:
                execution.fail('Marcado como falha pelo admin')
                count += 1
            except Exception:
                pass
        self.message_user(request, f'{count} execucao(oes) marcada(s) como falha.')
