#!/usr/bin/env python
"""
Script para testar importação de todos os pacotes principais do requirements.txt
Este script verifica se todas as dependências foram instaladas corretamente.
"""

import sys

# Lista de pacotes principais para testar
PACKAGES = {
    # Core Django
    'django': 'Django',
    'django.core.management': 'Django Management',
    
    # Database
    'psycopg2': 'PostgreSQL Driver',
    'dj_database_url': 'Database URL Parser',
    
    # Cache & Session
    'redis': 'Redis Client',
    'django_redis': 'Django Redis',
    
    # Celery
    'celery': 'Celery',
    'django_celery_beat': 'Django Celery Beat',
    'kombu': 'Kombu',
    'billiard': 'Billiard',
    
    # AI Agents
    'anthropic': 'Anthropic SDK',
    'openai': 'OpenAI SDK',
    
    # Authentication
    'allauth': 'Django Allauth',
    
    # Development
    'debug_toolbar': 'Django Debug Toolbar',
    'IPython': 'IPython',
    
    # Testing
    'pytest': 'Pytest',
    'pytest_django': 'Pytest Django',
    'pytest_cov': 'Pytest Coverage',
    'xdist': 'Pytest XDist',  # pytest-xdist importa como 'xdist'
    
    # Code Quality
    'black': 'Black',
    'ruff': 'Ruff',
    'mypy': 'MyPy',
    # django-stubs não tem módulo importável, é usado apenas pelo mypy
    
    # Utilities
    'dotenv': 'Python Dotenv',
    'PIL': 'Pillow',
    'corsheaders': 'Django CORS Headers',
    'whitenoise': 'WhiteNoise',
}

def test_imports():
    """Testa a importação de todos os pacotes."""
    failed_imports = []
    successful_imports = []
    
    print("=" * 70)
    print("Testando importação de pacotes do requirements.txt")
    print("=" * 70)
    print()
    
    for module_name, display_name in PACKAGES.items():
        try:
            __import__(module_name)
            print(f"✓ {display_name:30} ({module_name})")
            successful_imports.append(display_name)
        except ImportError as e:
            print(f"✗ {display_name:30} ({module_name}) - ERRO: {e}")
            failed_imports.append((display_name, module_name, str(e)))
        except Exception as e:
            print(f"⚠ {display_name:30} ({module_name}) - AVISO: {e}")
    
    print()
    print("=" * 70)
    print(f"Resultado: {len(successful_imports)}/{len(PACKAGES)} pacotes importados com sucesso")
    print("=" * 70)
    
    if failed_imports:
        print("\nPacotes que falharam na importação:")
        for display_name, module_name, error in failed_imports:
            print(f"  - {display_name} ({module_name}): {error}")
        return False
    
    return True

def test_version_compatibility():
    """Testa compatibilidade de versões principais."""
    print("\n" + "=" * 70)
    print("Verificando versões principais")
    print("=" * 70)
    print()
    
    try:
        import django
        django_version = django.get_version()
        print(f"Django: {django_version}")
        
        # Verificar se é Django 5.0+
        major_version = int(django_version.split('.')[0])
        if major_version >= 5:
            print("  ✓ Versão compatível (5.0+)")
        else:
            print(f"  ✗ Versão incompatível (requer 5.0+, encontrado {major_version}.x)")
            return False
    except Exception as e:
        print(f"  ✗ Erro ao verificar Django: {e}")
        return False
    
    try:
        import celery
        celery_version = celery.__version__
        print(f"Celery: {celery_version}")
        print("  ✓ Versão instalada")
    except Exception as e:
        print(f"  ✗ Erro ao verificar Celery: {e}")
        return False
    
    try:
        import redis
        redis_version = redis.__version__
        print(f"Redis: {redis_version}")
        print("  ✓ Versão instalada")
    except Exception as e:
        print(f"  ✗ Erro ao verificar Redis: {e}")
        return False
    
    try:
        import anthropic
        anthropic_version = anthropic.__version__
        print(f"Anthropic: {anthropic_version}")
        print("  ✓ Versão instalada")
    except Exception as e:
        print(f"  ✗ Erro ao verificar Anthropic: {e}")
        return False
    
    try:
        import openai
        openai_version = openai.__version__
        print(f"OpenAI: {openai_version}")
        print("  ✓ Versão instalada")
    except Exception as e:
        print(f"  ✗ Erro ao verificar OpenAI: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print()
    imports_ok = test_imports()
    versions_ok = test_version_compatibility()
    
    print()
    print("=" * 70)
    if imports_ok and versions_ok:
        print("✓ Todos os testes passaram com sucesso!")
        sys.exit(0)
    else:
        print("✗ Alguns testes falharam. Verifique os erros acima.")
        sys.exit(1)
