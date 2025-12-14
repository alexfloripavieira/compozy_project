"""
Base models for Compozy project.

This module contains abstract base models that are reused across all apps.
"""

from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    """
    Abstract base model that provides self-updating created_at and updated_at fields.

    All models that need timestamp tracking should inherit from this class.

    Attributes:
        created_at: DateTime when the record was created (auto-set on creation)
        updated_at: DateTime when the record was last updated (auto-set on save)
    """

    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        db_index=True,
        help_text='Data e hora de criacao do registro'
    )
    updated_at = models.DateTimeField(
        'atualizado em',
        auto_now=True,
        db_index=True,
        help_text='Data e hora da ultima atualizacao do registro'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """
        Override save to ensure updated_at is always set.

        Note: auto_now=True already handles this, but this override ensures
        consistency and allows for custom logic if needed.
        """
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
