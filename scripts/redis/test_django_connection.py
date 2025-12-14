#!/usr/bin/env python
"""
Script para testar conexão do Django com o Redis.
Execute com: python scripts/redis/test_django_connection.py
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

from django.core.cache import cache
from django.conf import settings
from django.contrib.sessions.backends.cache import SessionStore

def test_cache():
    """Testa a conexão com o cache Redis."""
    print("=" * 70)
    print("Teste de Conexão Django com Redis (Cache)")
    print("=" * 70)
    print()
    
    # Mostrar configuração do cache
    cache_config = settings.CACHES.get('default', {})
    print(f"Backend: {cache_config.get('BACKEND', 'N/A')}")
    print(f"Location: {cache_config.get('LOCATION', 'N/A')}")
    print()
    
    try:
        # Testar escrita
        test_key = 'compozy:test:connection'
        test_value = 'test_value_12345'
        cache.set(test_key, test_value, timeout=60)
        print("✓ Escrita no cache bem-sucedida")
        
        # Testar leitura
        retrieved_value = cache.get(test_key)
        if retrieved_value == test_value:
            print("✓ Leitura do cache bem-sucedida")
        else:
            print(f"✗ Erro: Valor lido ({retrieved_value}) não corresponde ao valor escrito ({test_value})")
            return False
        
        # Limpar chave de teste
        cache.delete(test_key)
        print("✓ Limpeza da chave de teste bem-sucedida")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao conectar ao cache Redis: {e}")
        print()
        print("Possíveis soluções:")
        print("1. Verifique se o Redis está rodando:")
        print("   - Docker: docker compose ps redis")
        print("   - Local: redis-cli ping")
        print()
        print("2. Verifique a REDIS_URL no arquivo .env:")
        print("   REDIS_URL=redis://127.0.0.1:6379/1")
        print()
        print("3. Execute o script de setup:")
        print("   ./scripts/redis/setup_redis.sh")
        return False

def test_session():
    """Testa a conexão com o backend de sessão Redis."""
    print()
    print("=" * 70)
    print("Teste de Conexão Django com Redis (Sessões)")
    print("=" * 70)
    print()
    
    # Mostrar configuração de sessão
    session_engine = getattr(settings, 'SESSION_ENGINE', 'N/A')
    session_cache_alias = getattr(settings, 'SESSION_CACHE_ALIAS', 'N/A')
    print(f"Session Engine: {session_engine}")
    print(f"Session Cache Alias: {session_cache_alias}")
    print()
    
    try:
        # Criar uma sessão de teste
        session = SessionStore()
        session['test_key'] = 'test_value'
        session.save()
        session_key = session.session_key
        print(f"✓ Sessão criada: {session_key}")
        
        # Recuperar a sessão
        retrieved_session = SessionStore(session_key=session_key)
        if retrieved_session.get('test_key') == 'test_value':
            print("✓ Sessão recuperada com sucesso")
        else:
            print("✗ Erro: Não foi possível recuperar a sessão")
            return False
        
        # Limpar sessão de teste
        retrieved_session.delete()
        print("✓ Sessão de teste removida")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao conectar ao backend de sessão Redis: {e}")
        print()
        print("Verifique se o Redis está configurado corretamente para sessões")
        return False

if __name__ == '__main__':
    cache_success = test_cache()
    session_success = test_session()
    
    print()
    print("=" * 70)
    if cache_success and session_success:
        print("✓ Todos os testes concluídos com sucesso!")
        sys.exit(0)
    else:
        print("✗ Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1)
