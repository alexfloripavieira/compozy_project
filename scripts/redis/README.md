# Scripts de Configuração e Gerenciamento do Redis

Este diretório contém scripts para configurar, gerenciar e monitorar o Redis do projeto Compozy.

## Requisitos

- Redis 7 (via Docker ou instalação local)
- Docker e Docker Compose (opcional, mas recomendado)

## Configuração Inicial

### Opção 1: Usando Docker (Recomendado)

1. Certifique-se de que o Docker está instalado e rodando
2. Execute o script de setup:
   ```bash
   ./scripts/redis/setup_redis.sh
   ```
   
   Ou inicie manualmente:
   ```bash
   docker compose up -d redis
   ```

3. O Redis será iniciado automaticamente na porta 6379

### Opção 2: Instalação Local

1. Instale Redis 7:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install redis-server
   
   # macOS (Homebrew)
   brew install redis
   brew services start redis
   ```

2. Inicie o serviço:
   ```bash
   # Ubuntu/Debian
   sudo systemctl start redis-server
   sudo systemctl enable redis-server
   
   # macOS
   brew services start redis
   ```

## Configuração do .env

Adicione a seguinte linha ao seu arquivo `.env`:

```bash
REDIS_URL=redis://127.0.0.1:6379/1
```

Para Celery (opcional, se usar URL diferente):
```bash
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
```

**Nota:** O banco de dados 1 é usado para cache/sessões, e o banco 0 pode ser usado para Celery.

## Testando a Conexão

### Via Script

```bash
./scripts/redis/test_connection.sh
```

### Via Django

```bash
python scripts/redis/test_django_connection.py
```

Este script testa tanto o cache quanto as sessões.

## Monitoramento

### Script de Monitoramento

```bash
# Ver menu de comandos
./scripts/redis/monitor.sh

# Testar conexão
./scripts/redis/monitor.sh ping

# Ver informações do servidor
./scripts/redis/monitor.sh info

# Ver estatísticas
./scripts/redis/monitor.sh stats

# Listar chaves (padrão: compozy:*)
./scripts/redis/monitor.sh keys 'compozy:*'

# Monitorar comandos em tempo real
./scripts/redis/monitor.sh monitor

# Abrir redis-cli interativo
./scripts/redis/monitor.sh cli
```

### Via redis-cli Diretamente

```bash
# Docker
docker compose exec redis redis-cli

# Local
redis-cli

# Comandos úteis:
#   PING - testa conexão
#   INFO - informações do servidor
#   KEYS compozy:* - lista chaves do projeto
#   FLUSHDB - limpa banco atual (CUIDADO!)
#   MONITOR - monitora comandos em tempo real
```

## Configuração no Django

O Redis está configurado em `config/settings/dev.py` e `config/settings/prod.py`:

### Cache
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
    }
}
```

### Sessões
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## Troubleshooting

### Erro: "Connection refused"

- Verifique se o Redis está rodando:
  ```bash
  # Docker
  docker compose ps redis
  
  # Local
  redis-cli ping
  ```

### Erro: "ModuleNotFoundError: No module named 'django_redis'"

- Instale as dependências:
  ```bash
  pip install -r requirements.txt
  ```

### Erro: "Authentication failed"

- Verifique a URL no arquivo `.env`
- Para Docker, não é necessário autenticação por padrão
- Para instalação local, verifique se há senha configurada

### Limpar Cache/Sessões

```bash
# Limpar banco de dados 1 (cache/sessões)
redis-cli -n 1 FLUSHDB

# Ou via Docker
docker compose exec redis redis-cli -n 1 FLUSHDB
```

**ATENÇÃO:** Isso apagará todos os dados do banco!

## Variáveis de Ambiente

Os scripts podem usar as seguintes variáveis de ambiente:

- `REDIS_HOST` - Host do Redis (padrão: `127.0.0.1`)
- `REDIS_PORT` - Porta (padrão: `6379`)
- `REDIS_DB` - Banco de dados (padrão: `1`)
- `REDIS_URL` - URL completa (formato: `redis://host:port/db`)

## Scripts Disponíveis

- `setup_redis.sh` - Configura Redis via Docker ou fornece instruções para instalação local
- `test_connection.sh` - Testa conexão com o Redis
- `monitor.sh` - Ferramenta de monitoramento e comandos úteis
- `test_django_connection.py` - Testa conexão do Django com Redis (cache e sessões)
