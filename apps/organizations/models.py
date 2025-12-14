"""
Organization and OrganizationMember models for Compozy.

This module contains the multi-tenant organization structure for the platform.
"""

import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse

from apps.common.models import TimestampedModel


class Organization(TimestampedModel):
    """
    Organization model representing a company or team.

    Organizations are the top-level entity for multi-tenancy.
    All problems, repositories, and tasks belong to an organization.

    Attributes:
        id: UUID primary key
        name: Organization display name
        slug: URL-friendly unique identifier
        description: Optional description
        logo_url: Optional URL to organization logo
        is_active: Whether the organization is active
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    name = models.CharField(
        'nome',
        max_length=255,
        help_text='Nome da organizacao'
    )
    slug = models.SlugField(
        'slug',
        max_length=100,
        unique=True,
        help_text='Identificador unico para URLs'
    )
    description = models.TextField(
        'descricao',
        blank=True,
        default='',
        help_text='Descricao da organizacao'
    )
    logo_url = models.URLField(
        'URL do logo',
        blank=True,
        default='',
        help_text='URL para o logo da organizacao'
    )
    is_active = models.BooleanField(
        'ativo',
        default=True,
        help_text='Se a organizacao esta ativa'
    )

    class Meta:
        verbose_name = 'Organizacao'
        verbose_name_plural = 'Organizacoes'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Return the URL for this organization's detail page."""
        return reverse('organizations:detail', kwargs={'slug': self.slug})

    def get_members(self):
        """Return all members of this organization."""
        return self.members.select_related('user').all()

    def get_admins(self):
        """Return all admin members of this organization."""
        return self.members.filter(role='admin').select_related('user')

    def is_member(self, user):
        """Check if a user is a member of this organization."""
        return self.members.filter(user=user).exists()

    def is_admin(self, user):
        """Check if a user is an admin of this organization."""
        return self.members.filter(user=user, role='admin').exists()


class OrganizationMember(TimestampedModel):
    """
    OrganizationMember model representing membership in an organization.

    Links users to organizations with role-based access control.

    Attributes:
        id: UUID primary key
        organization: Foreign key to Organization
        user: Foreign key to User
        role: Member role (admin, member, viewer)
        invited_by: User who invited this member
        joined_at: When the user joined
    """

    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('member', 'Membro'),
        ('viewer', 'Visualizador'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='organizacao'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        verbose_name='usuario'
    )
    role = models.CharField(
        'papel',
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        help_text='Papel do membro na organizacao'
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invitations_sent',
        verbose_name='convidado por'
    )
    joined_at = models.DateTimeField(
        'data de entrada',
        auto_now_add=True,
        help_text='Data em que o usuario entrou na organizacao'
    )

    class Meta:
        verbose_name = 'Membro da Organizacao'
        verbose_name_plural = 'Membros da Organizacao'
        ordering = ['-joined_at']
        unique_together = ['organization', 'user']
        indexes = [
            models.Index(fields=['organization', 'user']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.organization.name} ({self.get_role_display()})'

    def is_admin(self):
        """Check if this member is an admin."""
        return self.role == 'admin'

    def can_manage_members(self):
        """Check if this member can manage other members."""
        return self.role == 'admin'

    def can_create_problems(self):
        """Check if this member can create problems."""
        return self.role in ('admin', 'member')


class Repository(TimestampedModel):
    """
    Repository model representing a code repository linked to an organization.

    Supports multiple providers (GitHub, GitLab, Bitbucket) with authentication
    tokens for accessing private repositories.

    Attributes:
        id: UUID primary key
        organization: Foreign key to Organization
        name: Repository display name
        url: Full repository URL
        provider: Repository provider (github, gitlab, bitbucket)
        default_branch: Default branch name
        auth_token: Encrypted authentication token
        is_private: Whether the repository is private
        last_synced_at: Last time the repository was synced
        local_path: Local filesystem path for cloned repository
    """

    PROVIDER_CHOICES = [
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('bitbucket', 'Bitbucket'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='repositories',
        verbose_name='organizacao'
    )
    name = models.CharField(
        'nome',
        max_length=255,
        help_text='Nome do repositorio'
    )
    url = models.URLField(
        'URL do repositorio',
        max_length=500,
        help_text='URL completa do repositorio (ex: https://github.com/org/repo)'
    )
    provider = models.CharField(
        'provedor',
        max_length=20,
        choices=PROVIDER_CHOICES,
        default='github',
        help_text='Provedor do repositorio'
    )
    default_branch = models.CharField(
        'branch padrao',
        max_length=100,
        default='main',
        help_text='Nome da branch principal'
    )
    auth_token = models.CharField(
        'token de autenticacao',
        max_length=500,
        blank=True,
        default='',
        help_text='Token de acesso para repositorios privados (criptografado)'
    )
    is_private = models.BooleanField(
        'privado',
        default=False,
        help_text='Se o repositorio e privado'
    )
    last_synced_at = models.DateTimeField(
        'ultima sincronizacao',
        null=True,
        blank=True,
        help_text='Data da ultima sincronizacao do repositorio'
    )
    local_path = models.CharField(
        'caminho local',
        max_length=500,
        blank=True,
        default='',
        help_text='Caminho local onde o repositorio foi clonado'
    )

    class Meta:
        verbose_name = 'Repositorio'
        verbose_name_plural = 'Repositorios'
        ordering = ['name']
        unique_together = ['organization', 'url']
        indexes = [
            models.Index(fields=['organization', 'name']),
            models.Index(fields=['provider']),
        ]

    def __str__(self):
        return f'{self.name} ({self.get_provider_display()})'

    def get_absolute_url(self):
        """Return the URL for this repository's detail page."""
        return reverse('organizations:repository_detail', kwargs={
            'org_slug': self.organization.slug,
            'pk': self.pk
        })

    def get_clone_url(self):
        """
        Return the clone URL for this repository.

        If auth_token is set, returns an authenticated URL.
        Otherwise, returns the standard URL.
        """
        if self.auth_token and self.is_private:
            # Format authenticated URL based on provider
            if self.provider == 'github':
                # https://oauth2:token@github.com/org/repo.git
                url_parts = self.url.replace('https://', '').replace('http://', '')
                return f'https://oauth2:{self.auth_token}@{url_parts}.git'
            elif self.provider == 'gitlab':
                url_parts = self.url.replace('https://', '').replace('http://', '')
                return f'https://oauth2:{self.auth_token}@{url_parts}.git'
            elif self.provider == 'bitbucket':
                url_parts = self.url.replace('https://', '').replace('http://', '')
                return f'https://x-token-auth:{self.auth_token}@{url_parts}.git'
        return f'{self.url}.git' if not self.url.endswith('.git') else self.url

    def clone(self, target_path=None):
        """
        Clone this repository to a local path.

        Args:
            target_path: Optional target directory. If not provided, uses default.

        Returns:
            str: The path where the repository was cloned.

        Note:
            This method requires git to be installed and accessible.
            The actual cloning is handled by git_operations tool in production.
        """
        import subprocess
        import tempfile
        from pathlib import Path
        from django.utils import timezone

        if target_path is None:
            target_path = Path(tempfile.gettempdir()) / 'compozy_repos' / str(self.id)

        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        clone_url = self.get_clone_url()

        try:
            subprocess.run(
                ['git', 'clone', '--branch', self.default_branch, clone_url, str(target_path)],
                check=True,
                capture_output=True,
                text=True
            )
            self.local_path = str(target_path)
            self.last_synced_at = timezone.now()
            self.save(update_fields=['local_path', 'last_synced_at'])
            return str(target_path)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Failed to clone repository: {e.stderr}')

    def pull(self):
        """
        Pull latest changes from remote.

        Returns:
            bool: True if successful.

        Raises:
            Exception: If pull fails or repository not cloned.
        """
        import subprocess
        from pathlib import Path
        from django.utils import timezone

        if not self.local_path or not Path(self.local_path).exists():
            raise Exception('Repository not cloned locally')

        try:
            subprocess.run(
                ['git', '-C', self.local_path, 'pull', 'origin', self.default_branch],
                check=True,
                capture_output=True,
                text=True
            )
            self.last_synced_at = timezone.now()
            self.save(update_fields=['last_synced_at'])
            return True
        except subprocess.CalledProcessError as e:
            raise Exception(f'Failed to pull repository: {e.stderr}')
