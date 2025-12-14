#!/usr/bin/env python
"""
Script para testar conexão do Django com o banco de dados PostgreSQL.
Execute com: python scripts/db/test_django_connection.py
"""

import os
import sys
import django
from pathlib import Path

# Adicionar o diretório raiz do projeto ao path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.db import connection
from django.conf import settings

def test_connection():
    """Testa a conexão com o banco de dados."""
    print("=" * 70)
    print("Teste de Conexão Django com PostgreSQL")
    print("=" * 70)
    print()
    
    # Mostrar configuração do banco
    db_config = settings.DATABASES['default']
    print(f"Engine: {db_config.get('ENGINE', 'N/A')}")
    print(f"Name: {db_config.get('NAME', 'N/A')}")
    print(f"User: {db_config.get('USER', 'N/A')}")
    print(f"Host: {db_config.get('HOST', 'N/A')}")
    print(f"Port: {db_config.get('PORT', 'N/A')}")
    print()
    
    try:
        # Testar conexão
        with connection.cursor() as cursor:
            # Testar conexão básica
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            if result[0] == 1:
                print("✓ Conexão estabelecida com sucesso!")
                print()
                
                # Obter informações do banco
                cursor.execute("""
                    SELECT 
                        current_database() as database,
                        current_user as user,
                        version() as version,
                        current_setting('timezone') as timezone;
                """)
                
                info = cursor.fetchone()
                print("Informações do Banco de Dados:")
                print(f"  Database: {info[0]}")
                print(f"  User: {info[1]}")
                print(f"  Version: {info[2].split(',')[0]}")
                print(f"  Timezone: {info[3]}")
                print()
                
                # Verificar se o timezone está correto
                if info[3] == 'America/Sao_Paulo' or 'America/Sao_Paulo' in str(info[3]):
                    print("✓ Timezone configurado corretamente (America/Sao_Paulo)")
                else:
                    print(f"⚠ Timezone atual: {info[3]}")
                    print("  Para configurar: ALTER DATABASE compozy SET timezone = 'America/Sao_Paulo';")
                
                return True
            else:
                print("✗ Erro: Conexão estabelecida mas query retornou resultado inesperado")
                return False
                
    except Exception as e:
        print(f"✗ Erro ao conectar ao banco de dados: {e}")
        print()
        print("Possíveis soluções:")
        print("1. Verifique se o PostgreSQL está rodando:")
        print("   - Docker: docker compose ps db")
        print("   - Local: sudo systemctl status postgresql")
        print()
        print("2. Verifique a DATABASE_URL no arquivo .env:")
        print("   DATABASE_URL=postgresql://compozy:compozy_dev_password@localhost:5432/compozy")
        print()
        print("3. Execute o script de setup:")
        print("   ./scripts/db/setup_postgres.sh")
        return False

if __name__ == '__main__':
    success = test_connection()
    print()
    print("=" * 70)
    if success:
        print("✓ Teste concluído com sucesso!")
        sys.exit(0)
    else:
        print("✗ Teste falhou. Verifique os erros acima.")
        sys.exit(1)
