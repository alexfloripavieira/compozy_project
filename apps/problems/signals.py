"""
Signal handlers for the Problems app.

This module contains Django signal handlers that respond to model events,
particularly for logging status changes on Problem instances.
"""

import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.problems.models import Problem


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Problem)
def problem_pre_save(sender, instance, **kwargs):
    """
    Signal handler that runs before a Problem is saved.

    Captures the old status for comparison in post_save signal.
    Stores the old status in a temporary attribute on the instance.

    Args:
        sender: The model class (Problem)
        instance: The Problem instance being saved
        **kwargs: Additional keyword arguments from the signal
    """
    if instance.pk:
        try:
            old_instance = Problem.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Problem.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Problem)
def problem_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that runs after a Problem is saved.

    Logs status changes for audit trail and debugging purposes.

    Args:
        sender: The model class (Problem)
        instance: The Problem instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments from the signal
    """
    if created:
        logger.info(
            f"Problem created: '{instance.title}' (id={instance.pk}) "
            f"by user {instance.created_by} in organization {instance.organization}"
        )
        logger.info(
            f"Problem '{instance.title}' initial status: {instance.status}"
        )
    else:
        old_status = getattr(instance, '_old_status', None)
        if old_status and old_status != instance.status:
            logger.info(
                f"Problem '{instance.title}' (id={instance.pk}) "
                f"status changed: '{old_status}' -> '{instance.status}'"
            )

            # Log additional context for specific transitions
            if instance.status == 'failed':
                logger.warning(
                    f"Problem '{instance.title}' (id={instance.pk}) failed. "
                    f"Error: {instance.error_message or 'No error message provided'}"
                )
            elif instance.status == 'completed':
                logger.info(
                    f"Problem '{instance.title}' (id={instance.pk}) "
                    f"completed successfully!"
                )
            elif instance.status == 'cancelled':
                logger.info(
                    f"Problem '{instance.title}' (id={instance.pk}) "
                    f"was cancelled by user."
                )


@receiver(post_save, sender=Problem)
def problem_status_notification(sender, instance, created, **kwargs):
    """
    Signal handler for sending notifications on status changes.

    This handler can be extended to send email notifications,
    webhook calls, or other notification mechanisms.

    Args:
        sender: The model class (Problem)
        instance: The Problem instance that was saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments from the signal
    """
    # Skip notifications for new instances (they get their own notification)
    if created:
        return

    old_status = getattr(instance, '_old_status', None)
    if old_status and old_status != instance.status:
        # Status transitions that might need notifications
        notification_statuses = {
            'prd_review': 'PRD pronto para revisao',
            'spec_review': 'Especificacao tecnica pronta para revisao',
            'task_selection': 'Tarefas prontas para selecao',
            'completed': 'Problema concluido com sucesso',
            'failed': 'Problema falhou durante processamento',
        }

        if instance.status in notification_statuses:
            message = notification_statuses[instance.status]
            logger.debug(
                f"Notification triggered for Problem '{instance.title}': {message}"
            )
            # TODO: Implement actual notification sending
            # Examples:
            # - Send email to instance.created_by
            # - Send webhook to external service
            # - Create in-app notification
