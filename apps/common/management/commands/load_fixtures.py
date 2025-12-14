"""
Management command para carregar fixtures de dados de teste.

Este comando carrega o arquivo fixtures/initial_data.json que contem
dados de demonstracao para o sistema Compozy.

Usage:
    python manage.py load_fixtures
    python manage.py load_fixtures --clear  # Limpa dados antes de carregar
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import connection
import os


User = get_user_model()


class Command(BaseCommand):
    help = 'Carrega fixtures de dados de teste para o sistema Compozy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpa os dados existentes antes de carregar as fixtures',
        )
        parser.add_argument(
            '--fixture',
            type=str,
            default='initial_data',
            help='Nome do arquivo de fixture (sem extensao .json)',
        )

    def handle(self, *args, **options):
        fixture_name = options['fixture']
        clear_data = options['clear']

        # Verificar se o arquivo existe
        from django.conf import settings
        fixture_path = os.path.join(settings.BASE_DIR, 'fixtures', f'{fixture_name}.json')
        
        if not os.path.exists(fixture_path):
            raise CommandError(f'Arquivo de fixture nao encontrado: {fixture_path}')

        self.stdout.write(self.style.NOTICE(f'Carregando fixtures de: {fixture_path}'))

        if clear_data:
            self.stdout.write(self.style.WARNING('Limpando dados existentes...'))
            self._clear_fixture_data()

        try:
            # Usar o comando loaddata do Django
            call_command('loaddata', fixture_name, verbosity=options['verbosity'])
            
            self.stdout.write(self.style.SUCCESS('Fixtures carregadas com sucesso!'))
            
            # Mostrar resumo dos dados carregados
            self._show_summary()
            
        except Exception as e:
            raise CommandError(f'Erro ao carregar fixtures: {str(e)}')

    def _clear_fixture_data(self):
        """Remove dados existentes das tabelas de fixture."""
        from apps.chat.models import ChatMessage
        from apps.tasks_app.models import Task, TaskExecution
        from apps.documents.models import PRDDocument, TechSpecDocument
        from apps.problems.models import Problem
        from apps.organizations.models import Repository, OrganizationMember, Organization

        # Ordem importante devido a foreign keys
        models_to_clear = [
            ('ChatMessage', ChatMessage),
            ('TaskExecution', TaskExecution),
            ('Task', Task),
            ('TechSpecDocument', TechSpecDocument),
            ('PRDDocument', PRDDocument),
            ('Problem', Problem),
            ('Repository', Repository),
            ('OrganizationMember', OrganizationMember),
            ('Organization', Organization),
        ]

        for name, model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'  - {name}: {count} registros removidos')

        # Remover usuarios de teste (pk >= 100)
        demo_users = User.objects.filter(pk__gte=100, pk__lt=1000)
        user_count = demo_users.count()
        if user_count > 0:
            demo_users.delete()
            self.stdout.write(f'  - User (demo): {user_count} registros removidos')

    def _show_summary(self):
        """Mostra resumo dos dados carregados."""
        from apps.chat.models import ChatMessage
        from apps.tasks_app.models import Task, TaskExecution
        from apps.documents.models import PRDDocument, TechSpecDocument
        from apps.problems.models import Problem
        from apps.organizations.models import Repository, OrganizationMember, Organization

        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('Resumo dos dados carregados:'))
        self.stdout.write(f'  - Usuarios: {User.objects.count()}')
        self.stdout.write(f'  - Organizacoes: {Organization.objects.count()}')
        self.stdout.write(f'  - Membros: {OrganizationMember.objects.count()}')
        self.stdout.write(f'  - Repositorios: {Repository.objects.count()}')
        self.stdout.write(f'  - Problemas: {Problem.objects.count()}')
        self.stdout.write(f'  - PRDs: {PRDDocument.objects.count()}')
        self.stdout.write(f'  - Tech Specs: {TechSpecDocument.objects.count()}')
        self.stdout.write(f'  - Tarefas: {Task.objects.count()}')
        self.stdout.write(f'  - Execucoes: {TaskExecution.objects.count()}')
        self.stdout.write(f'  - Mensagens Chat: {ChatMessage.objects.count()}')
        self.stdout.write('')
