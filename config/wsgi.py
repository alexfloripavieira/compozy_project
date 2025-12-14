"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Security: In production, DJANGO_SETTINGS_MODULE must be explicitly set
# For local development, default to dev settings
# Detect production environment to prevent accidental use of dev settings
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    # Only check for explicit production environment indicator
    # DEBUG flag is not used as it may be set to False for testing purposes
    environment = os.environ.get('ENVIRONMENT', '').lower()
    is_production = environment == 'production'
    
    if is_production:
        # In production environment, require explicit configuration
        # This prevents accidental use of dev settings which would enable DEBUG=True
        raise ValueError(
            'DJANGO_SETTINGS_MODULE must be explicitly set in production. '
            'Set DJANGO_SETTINGS_MODULE=config.settings.prod'
        )
    else:
        # Default to dev for local development
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

application = get_wsgi_application()
