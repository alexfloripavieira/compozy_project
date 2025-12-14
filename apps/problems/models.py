"""
Problem model for tracking issues and features to be implemented.

This module defines the Problem model which represents an issue or feature
that needs to be implemented. It includes a status workflow that tracks
the progress through PRD generation, tech spec generation, task creation,
and implementation phases.
"""

import uuid
import logging

from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.common.models import TimestampedModel
from apps.organizations.models import Organization, Repository


logger = logging.getLogger(__name__)
User = get_user_model()


class Problem(TimestampedModel):
    """
    Problem model representing an issue or feature to be implemented.

    Problems go through a workflow of states from initial draft through
    PRD generation, tech spec generation, task creation, and finally
    implementation.

    Attributes:
        id: UUID primary key
        organization: The organization this problem belongs to
        created_by: User who created the problem
        title: Brief title describing the problem
        description: Detailed description of the problem/feature
        status: Current workflow status
        priority: Priority level (low, medium, high, critical)
        repositories: Repositories involved in solving this problem
        workflow_id: Optional ID linking to Celery workflow
        error_message: Error message if status is 'failed'
    """

    # Status workflow choices
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('analyzing', 'Analisando'),
        ('prd_generation', 'Gerando PRD'),
        ('prd_review', 'Revisao de PRD'),
        ('spec_generation', 'Gerando Especificacao'),
        ('spec_review', 'Revisao de Especificacao'),
        ('task_creation', 'Criando Tarefas'),
        ('task_selection', 'Selecao de Tarefas'),
        ('executing', 'Executando'),
        ('testing', 'Testando'),
        ('completed', 'Concluido'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelado'),
    ]

    # Priority choices
    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Critica'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='problems',
        verbose_name='organizacao',
        help_text='Organizacao a qual este problema pertence'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_problems',
        verbose_name='criado por',
        help_text='Usuario que criou o problema'
    )
    title = models.CharField(
        'titulo',
        max_length=255,
        help_text='Titulo breve descrevendo o problema'
    )
    description = models.TextField(
        'descricao',
        help_text='Descricao detalhada do problema ou feature'
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True,
        help_text='Status atual do workflow'
    )
    priority = models.CharField(
        'prioridade',
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        db_index=True,
        help_text='Nivel de prioridade do problema'
    )
    repositories = models.ManyToManyField(
        Repository,
        related_name='problems',
        verbose_name='repositorios',
        blank=True,
        help_text='Repositorios envolvidos na solucao deste problema'
    )
    workflow_id = models.CharField(
        'ID do workflow',
        max_length=255,
        blank=True,
        default='',
        help_text='ID do workflow Celery associado'
    )
    error_message = models.TextField(
        'mensagem de erro',
        blank=True,
        default='',
        help_text='Mensagem de erro se o status for "failed"'
    )

    class Meta:
        verbose_name = 'Problema'
        verbose_name_plural = 'Problemas'
        ordering = ['-created_at', 'priority']
        db_table = 'problems_problem'
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'priority']),
            models.Index(fields=['created_by', 'status']),
            models.Index(fields=['status', 'priority']),
        ]

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'

    def get_absolute_url(self):
        """Return the URL for this problem's detail page."""
        return reverse('problems:detail', kwargs={
            'org_slug': self.organization.slug,
            'pk': self.pk
        })

    # Status workflow methods
    def can_transition_to(self, new_status):
        """
        Check if transition to new_status is valid from current status.

        Args:
            new_status: The target status to transition to.

        Returns:
            bool: True if transition is valid, False otherwise.
        """
        valid_transitions = {
            'draft': ['analyzing', 'cancelled'],
            'analyzing': ['prd_generation', 'failed', 'cancelled'],
            'prd_generation': ['prd_review', 'failed', 'cancelled'],
            'prd_review': ['spec_generation', 'prd_generation', 'cancelled'],
            'spec_generation': ['spec_review', 'failed', 'cancelled'],
            'spec_review': ['task_creation', 'spec_generation', 'cancelled'],
            'task_creation': ['task_selection', 'failed', 'cancelled'],
            'task_selection': ['executing', 'cancelled'],
            'executing': ['testing', 'failed', 'cancelled'],
            'testing': ['completed', 'executing', 'failed', 'cancelled'],
            'completed': [],  # Terminal state
            'failed': ['draft'],  # Can retry from draft
            'cancelled': ['draft'],  # Can reopen
        }
        return new_status in valid_transitions.get(self.status, [])

    def transition_to(self, new_status, error_message=''):
        """
        Transition to a new status if valid.

        Args:
            new_status: The target status.
            error_message: Optional error message (used when transitioning to 'failed').

        Returns:
            bool: True if transition was successful.

        Raises:
            ValueError: If transition is not valid.
        """
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Transicao invalida de '{self.status}' para '{new_status}'"
            )

        old_status = self.status
        self.status = new_status

        if new_status == 'failed' and error_message:
            self.error_message = error_message
        elif new_status != 'failed':
            self.error_message = ''

        self.save(update_fields=['status', 'error_message', 'updated_at'])

        logger.info(
            f"Problem '{self.title}' (id={self.pk}) transitioned from "
            f"'{old_status}' to '{new_status}'"
        )
        return True

    def start_analysis(self):
        """Start the analysis workflow from draft state."""
        return self.transition_to('analyzing')

    def mark_failed(self, error_message):
        """Mark the problem as failed with an error message."""
        return self.transition_to('failed', error_message=error_message)

    def cancel(self):
        """Cancel the problem."""
        return self.transition_to('cancelled')

    def reopen(self):
        """Reopen a failed or cancelled problem."""
        return self.transition_to('draft')

    # Helper properties
    @property
    def is_active(self):
        """Check if the problem is in an active (non-terminal) state."""
        return self.status not in ['completed', 'failed', 'cancelled']

    @property
    def is_terminal(self):
        """Check if the problem is in a terminal state."""
        return self.status in ['completed', 'failed', 'cancelled']

    @property
    def is_in_progress(self):
        """Check if work is currently being done on the problem."""
        return self.status in [
            'analyzing', 'prd_generation', 'spec_generation',
            'task_creation', 'executing', 'testing'
        ]

    @property
    def is_awaiting_review(self):
        """Check if the problem is waiting for user review."""
        return self.status in ['prd_review', 'spec_review', 'task_selection']

    def get_progress_percentage(self):
        """
        Calculate approximate progress through the workflow.

        Returns:
            int: Progress percentage (0-100).
        """
        progress_map = {
            'draft': 0,
            'analyzing': 10,
            'prd_generation': 20,
            'prd_review': 30,
            'spec_generation': 40,
            'spec_review': 50,
            'task_creation': 60,
            'task_selection': 70,
            'executing': 80,
            'testing': 90,
            'completed': 100,
            'failed': 0,
            'cancelled': 0,
        }
        return progress_map.get(self.status, 0)
