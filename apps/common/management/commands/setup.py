"""
Comando Django para configurar automaticamente o ambiente de desenvolvimento.
Execute: python manage.py setup
"""

import os
import subprocess
import sys
import time
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Configura automaticamente o ambiente de desenvolvimento (Docker, .env, migrações)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-docker',
            action='store_true',
            help='Pula a inicialização dos serviços Docker',
        )
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Pula a execução das migrações',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🚀 Configuração Automática do Compozy'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # 1. Verificar e configurar Docker
        if not options['skip_docker']:
            self.setup_docker()
        else:
            self.stdout.write(self.style.WARNING('⏭️  Pulando configuração do Docker'))

        # 2. Configurar .env
        self.setup_env()

        # 3. Testar conexões
        self.test_connections()

        # 4. Executar migrações
        if not options['skip_migrations']:
            self.run_migrations()
        else:
            self.stdout.write(self.style.WARNING('⏭️  Pulando migrações'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('✅ Configuração concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write('Agora você pode executar:')
        self.stdout.write(self.style.SUCCESS('  python manage.py runserver'))
        self.stdout.write('')

    def setup_docker(self):
        """Inicia os serviços Docker (PostgreSQL e Redis)."""
        self.stdout.write(self.style.SUCCESS('📦 Configurando Docker...'))

        # Verificar se Docker está disponível
        docker_cmd = None

        # Tentar docker compose (versão nova - Docker Compose V2)
        if self._command_exists('docker'):
            result = subprocess.run(
                ['docker', 'compose', 'version'],
                capture_output=True,
                check=False
            )
            if result.returncode == 0:
                docker_cmd = ['docker', 'compose']
                self.stdout.write('   Usando: docker compose')
        
        # Tentar docker-compose (versão antiga - Docker Compose V1)
        if not docker_cmd and self._command_exists('docker-compose'):
            docker_cmd = ['docker-compose']
            self.stdout.write('   Usando: docker-compose')

        if not docker_cmd:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Docker Compose não encontrado.'
                )
            )
            self.stdout.write(
                '   Instale Docker Desktop ou docker-compose para usar os serviços automaticamente.'
            )
            self.stdout.write(
                '   Ou configure PostgreSQL e Redis manualmente e use: --skip-docker'
            )
            return

        # Verificar se docker-compose.yml existe
        if not Path('docker-compose.yml').exists():
            self.stdout.write(
                self.style.ERROR('❌ docker-compose.yml não encontrado!')
            )
            return

        # Iniciar serviços
        self.stdout.write('   Iniciando PostgreSQL e Redis...')
        result = self._run_command(docker_cmd + ['up', '-d', 'db', 'redis'], check=False)

        if result:
            self.stdout.write('   Aguardando serviços iniciarem (5 segundos)...')
            time.sleep(5)

            # Verificar se estão rodando
            ps_result = subprocess.run(
                docker_cmd + ['ps', '--format', 'json'],
                capture_output=True,
                text=True,
                check=False
            )
            
            if 'compozy_postgres' in ps_result.stdout or 'Up' in ps_result.stdout:
                self.stdout.write(self.style.SUCCESS('   ✅ PostgreSQL está rodando'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  PostgreSQL pode não estar pronto'))

            if 'compozy_redis' in ps_result.stdout or 'Up' in ps_result.stdout:
                self.stdout.write(self.style.SUCCESS('   ✅ Redis está rodando'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Redis pode não estar pronto'))
        else:
            self.stdout.write(
                self.style.WARNING('   ⚠️  Erro ao iniciar serviços Docker')
            )
            self.stdout.write(
                '   Verifique se o Docker está rodando: docker ps'
            )

    def setup_env(self):
        """Cria ou atualiza o arquivo .env com as configurações necessárias."""
        self.stdout.write(self.style.SUCCESS('📝 Configurando arquivo .env...'))

        env_path = Path('.env')
        env_example_path = Path('.env.example')

        # Valores padrão
        default_values = {
            'DATABASE_URL': 'postgresql://compozy:compozy_dev_password@localhost:5432/compozy',
            'REDIS_URL': 'redis://127.0.0.1:6379/1',
            'CELERY_BROKER_URL': 'redis://127.0.0.1:6379/1',
            'CELERY_RESULT_BACKEND': 'redis://127.0.0.1:6379/1',
            'SECRET_KEY': 'django-insecure-dev-key-change-in-production',
            'DEBUG': 'True',
            'ALLOWED_HOSTS': 'localhost,127.0.0.1',
        }

        # Se .env não existe, criar a partir do exemplo ou com valores padrão
        if not env_path.exists():
            if env_example_path.exists():
                self.stdout.write('   Copiando .env.example para .env...')
                import shutil
                shutil.copy(env_example_path, env_path)
            else:
                self.stdout.write('   Criando .env com valores padrão...')
                with open(env_path, 'w') as f:
                    f.write('# Configuração do ambiente de desenvolvimento\n')
                    f.write('# Gerado automaticamente por: python manage.py setup\n\n')
                    for key, value in default_values.items():
                        f.write(f'{key}={value}\n')

            self.stdout.write(self.style.SUCCESS('   ✅ Arquivo .env criado'))
        else:
            # Verificar se DATABASE_URL está configurado
            env_content = env_path.read_text()
            if 'DATABASE_URL' not in env_content:
                self.stdout.write('   Adicionando DATABASE_URL ao .env...')
                with open(env_path, 'a') as f:
                    f.write(f'\nDATABASE_URL={default_values["DATABASE_URL"]}\n')
                self.stdout.write(self.style.SUCCESS('   ✅ DATABASE_URL adicionado'))
            else:
                self.stdout.write('   ✅ Arquivo .env já existe e está configurado')

    def test_connections(self):
        """Testa conexões com PostgreSQL e Redis."""
        self.stdout.write(self.style.SUCCESS('🔌 Testando conexões...'))

        # Testar PostgreSQL
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] == 1:
                    self.stdout.write(self.style.SUCCESS('   ✅ PostgreSQL: Conectado'))
                else:
                    self.stdout.write(self.style.ERROR('   ❌ PostgreSQL: Erro na conexão'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ PostgreSQL: {str(e)}')
            )
            self.stdout.write(
                '   💡 Dica: Verifique se o PostgreSQL está rodando e o .env está configurado'
            )

        # Testar Redis
        try:
            import redis
            r = redis.from_url(settings.CACHES['default']['LOCATION'])
            r.ping()
            self.stdout.write(self.style.SUCCESS('   ✅ Redis: Conectado'))
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'   ⚠️  Redis: {str(e)}')
            )
            self.stdout.write(
                '   💡 Dica: Verifique se o Redis está rodando'
            )

    def run_migrations(self):
        """Executa as migrações do Django."""
        self.stdout.write(self.style.SUCCESS('🗄️  Executando migrações...'))

        # Verificar se há migrações pendentes
        result = self._run_command(
            [sys.executable, 'manage.py', 'makemigrations'],
            check=False
        )

        if result:
            self.stdout.write('   Migrações criadas/atualizadas')

        # Aplicar migrações
        result = self._run_command(
            [sys.executable, 'manage.py', 'migrate'],
            check=False
        )

        if result:
            self.stdout.write(self.style.SUCCESS('   ✅ Migrações aplicadas'))
        else:
            self.stdout.write(
                self.style.WARNING('   ⚠️  Erro ao aplicar migrações')
            )

    def _command_exists(self, command):
        """Verifica se um comando existe no PATH."""
        return subprocess.run(
            ['which', command],
            capture_output=True,
            check=False
        ).returncode == 0

    def _run_command(self, command, check=True, show_output=False):
        """Executa um comando e retorna True se bem-sucedido."""
        try:
            result = subprocess.run(
                command,
                capture_output=not show_output,
                text=True,
                check=check
            )
            if show_output and result.stdout:
                self.stdout.write(result.stdout)
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            if show_output:
                self.stdout.write(self.style.ERROR(f'Erro: {e}'))
            return False
