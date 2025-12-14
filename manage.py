#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
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
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
