"""
Comando para verificar e configurar o ambiente de desenvolvimento.
Execute: python manage.py setup
"""

import sys
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Verifica conexões e executa migrações'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check',
            action='store_true',
            help='Apenas verifica conexões, não executa migrações',
        )

    def handle(self, *args, **options):
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('  Compozy - Setup'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')

        # Verificar conexões
        pg_ok = self._check_postgres()
        redis_ok = self._check_redis()

        if not pg_ok or not redis_ok:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('Corrija os erros acima antes de continuar.'))
            self.stdout.write('Veja DEV_SETUP.md para instruções de instalação.')
            return

        if options['check']:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('Tudo OK!'))
            return

        # Executar migrações
        self.stdout.write('')
        self._run_migrations()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('  Setup concluído!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('Execute: python manage.py runserver')
        self.stdout.write('')

    def _check_postgres(self):
        """Verifica conexão com PostgreSQL."""
        self.stdout.write('PostgreSQL... ', ending='')
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('OK'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR('ERRO'))
            self.stdout.write(f'  {str(e)[:60]}')
            return False

    def _check_redis(self):
        """Verifica conexão com Redis."""
        self.stdout.write('Redis...      ', ending='')
        try:
            import redis
            r = redis.from_url(settings.CACHES['default']['LOCATION'])
            r.ping()
            self.stdout.write(self.style.SUCCESS('OK'))
            return True
        except Exception as e:
            self.stdout.write(self.style.ERROR('ERRO'))
            self.stdout.write(f'  {str(e)[:60]}')
            return False

    def _run_migrations(self):
        """Executa migrações."""
        from django.core.management import call_command

        self.stdout.write('Migrações... ', ending='')
        try:
            call_command('migrate', verbosity=0)
            self.stdout.write(self.style.SUCCESS('OK'))
        except Exception as e:
            self.stdout.write(self.style.ERROR('ERRO'))
            self.stdout.write(f'  {e}')
