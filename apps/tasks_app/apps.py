"""
App configuration for the tasks_app Django application.
"""
from django.apps import AppConfig


class TasksAppConfig(AppConfig):
    """Configuration for the Tasks application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks_app'
    verbose_name = 'Tarefas'

    def ready(self):
        """
        Run code when the app is ready.

        This is used to import signals and other startup code.
        """
        pass  # Signals can be imported here when needed
