"""
Chat models for agent-user conversations.

This module contains the ChatMessage model for storing conversations
between users and AI agents during the problem-solving workflow.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model

from apps.common.models import TimestampedModel
from apps.problems.models import Problem

User = get_user_model()


class ChatMessage(TimestampedModel):
    """
    ChatMessage model for conversations between agents and users.

    Used primarily during PRD generation and clarification phases where
    the Business Analyst agent may need to ask questions to the user
    and receive responses.

    Attributes:
        id: UUID primary key
        problem: The problem this message is associated with
        sender_type: Type of sender (user or agent)
        sender_user: User who sent the message (if sender_type is 'user')
        agent_name: Name of the agent (if sender_type is 'agent')
        content: The message content
        message_type: Type of message (question, answer, info, error)
        metadata: Optional JSON metadata for additional context
    """

    # Sender type choices
    SENDER_TYPE_CHOICES = [
        ('user', 'Usuario'),
        ('agent', 'Agente'),
    ]

    # Message type choices
    MESSAGE_TYPE_CHOICES = [
        ('question', 'Pergunta'),
        ('answer', 'Resposta'),
        ('info', 'Informacao'),
        ('error', 'Erro'),
        ('system', 'Sistema'),
    ]

    # Agent name choices
    AGENT_NAME_CHOICES = [
        ('business_analyst', 'Business Analyst'),
        ('tech_architect', 'Tech Architect'),
        ('task_planner', 'Task Planner'),
        ('code_writer', 'Code Writer'),
        ('test_runner', 'Test Runner'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    problem = models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        verbose_name='problema',
        help_text='Problema ao qual esta mensagem esta associada'
    )
    sender_type = models.CharField(
        'tipo de remetente',
        max_length=10,
        choices=SENDER_TYPE_CHOICES,
        db_index=True,
        help_text='Tipo de remetente da mensagem (usuario ou agente)'
    )
    sender_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_messages',
        verbose_name='usuario remetente',
        help_text='Usuario que enviou a mensagem (se sender_type for user)'
    )
    agent_name = models.CharField(
        'nome do agente',
        max_length=50,
        choices=AGENT_NAME_CHOICES,
        blank=True,
        default='',
        help_text='Nome do agente que enviou a mensagem (se sender_type for agent)'
    )
    content = models.TextField(
        'conteudo',
        help_text='Conteudo da mensagem'
    )
    message_type = models.CharField(
        'tipo de mensagem',
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='info',
        db_index=True,
        help_text='Tipo da mensagem'
    )
    metadata = models.JSONField(
        'metadados',
        default=dict,
        blank=True,
        help_text='Metadados adicionais em formato JSON'
    )
    is_read = models.BooleanField(
        'lida',
        default=False,
        help_text='Indica se a mensagem foi lida'
    )

    class Meta:
        verbose_name = 'Mensagem de Chat'
        verbose_name_plural = 'Mensagens de Chat'
        ordering = ['created_at']
        db_table = 'chat_chatmessage'
        indexes = [
            models.Index(fields=['problem', 'created_at']),
            models.Index(fields=['problem', 'sender_type']),
            models.Index(fields=['sender_user', 'created_at']),
        ]

    def __str__(self):
        sender = self.sender_user.username if self.sender_type == 'user' else self.agent_name
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f'[{sender}] {content_preview}'

    @property
    def sender_display_name(self):
        """Return a display-friendly name for the sender."""
        if self.sender_type == 'user':
            return self.sender_user.get_full_name() or self.sender_user.username if self.sender_user else 'Usuario'
        return dict(self.AGENT_NAME_CHOICES).get(self.agent_name, self.agent_name)

    @property
    def is_from_agent(self):
        """Check if the message was sent by an agent."""
        return self.sender_type == 'agent'

    @property
    def is_from_user(self):
        """Check if the message was sent by a user."""
        return self.sender_type == 'user'

    def mark_as_read(self):
        """Mark the message as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read', 'updated_at'])

    @classmethod
    def create_agent_message(cls, problem, agent_name, content, message_type='info', metadata=None):
        """
        Factory method to create an agent message.

        Args:
            problem: The Problem instance
            agent_name: Name of the agent sending the message
            content: Message content
            message_type: Type of message (default: 'info')
            metadata: Optional metadata dict

        Returns:
            ChatMessage instance
        """
        return cls.objects.create(
            problem=problem,
            sender_type='agent',
            agent_name=agent_name,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )

    @classmethod
    def create_user_message(cls, problem, user, content, message_type='answer', metadata=None):
        """
        Factory method to create a user message.

        Args:
            problem: The Problem instance
            user: The User instance sending the message
            content: Message content
            message_type: Type of message (default: 'answer')
            metadata: Optional metadata dict

        Returns:
            ChatMessage instance
        """
        return cls.objects.create(
            problem=problem,
            sender_type='user',
            sender_user=user,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
