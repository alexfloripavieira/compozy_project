"""
Django admin configuration for organizations app.
"""

from django.contrib import admin
from .models import Organization, OrganizationMember, Repository


class OrganizationMemberInline(admin.TabularInline):
    """Inline admin for organization members."""
    model = OrganizationMember
    extra = 0
    autocomplete_fields = ['user', 'invited_by']
    readonly_fields = ['joined_at']


class RepositoryInline(admin.TabularInline):
    """Inline admin for organization repositories."""
    model = Repository
    extra = 0
    readonly_fields = ['last_synced_at']
    fields = ['name', 'url', 'provider', 'default_branch', 'is_private', 'last_synced_at']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin configuration for Organization model."""

    list_display = ['name', 'slug', 'is_active', 'member_count', 'repository_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [OrganizationMemberInline, RepositoryInline]

    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'slug', 'description')
        }),
        ('Configuracoes', {
            'fields': ('logo_url', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def member_count(self, obj):
        """Return the number of members in the organization."""
        return obj.members.count()
    member_count.short_description = 'Membros'

    def repository_count(self, obj):
        """Return the number of repositories in the organization."""
        return obj.repositories.count()
    repository_count.short_description = 'Repositorios'


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    """Admin configuration for OrganizationMember model."""

    list_display = ['user', 'organization', 'role', 'joined_at']
    list_filter = ['role', 'joined_at', 'organization']
    search_fields = ['user__username', 'user__email', 'organization__name']
    autocomplete_fields = ['user', 'organization', 'invited_by']
    readonly_fields = ['id', 'joined_at', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('id', 'organization', 'user', 'role')
        }),
        ('Convite', {
            'fields': ('invited_by', 'joined_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    """Admin configuration for Repository model."""

    list_display = ['name', 'organization', 'provider', 'default_branch', 'is_private', 'last_synced_at']
    list_filter = ['provider', 'is_private', 'organization', 'created_at']
    search_fields = ['name', 'url', 'organization__name']
    autocomplete_fields = ['organization']
    readonly_fields = ['id', 'last_synced_at', 'local_path', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('id', 'organization', 'name', 'url')
        }),
        ('Configuracao do Repositorio', {
            'fields': ('provider', 'default_branch', 'is_private')
        }),
        ('Autenticacao', {
            'fields': ('auth_token',),
            'classes': ('collapse',),
            'description': 'Token de acesso para repositorios privados.'
        }),
        ('Status', {
            'fields': ('last_synced_at', 'local_path'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
