#!/bin/bash
# Script para monitorar Redis usando redis-cli
# Uso: ./monitor.sh [comando]
# Comandos disponíveis: ping, info, stats, keys, monitor, cli

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configurações
REDIS_HOST=${REDIS_HOST:-127.0.0.1}
REDIS_PORT=${REDIS_PORT:-6379}
REDIS_DB=${REDIS_DB:-1}

# Verificar se está usando Docker
USE_DOCKER=false
if command -v docker &> /dev/null || command -v docker-compose &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        if docker-compose ps redis 2>/dev/null | grep -q "Up"; then
            USE_DOCKER=true
        fi
    elif command -v docker &> /dev/null; then
        if docker compose ps redis 2>/dev/null | grep -q "Up"; then
            USE_DOCKER=true
        fi
    fi
fi

# Função para executar comando Redis
run_redis_command() {
    local cmd="$1"
    
    if [ "$USE_DOCKER" = true ]; then
        if command -v docker-compose &> /dev/null; then
            docker-compose exec -T redis redis-cli "$cmd"
        else
            docker compose exec -T redis redis-cli "$cmd"
        fi
    else
        if ! command -v redis-cli &> /dev/null; then
            echo -e "${RED}Erro: redis-cli não encontrado!${NC}"
            exit 1
        fi
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" "$cmd"
    fi
}

# Se nenhum comando foi passado, mostrar menu
if [ $# -eq 0 ]; then
    echo -e "${GREEN}=== Monitor Redis - Compozy ===${NC}\n"
    echo -e "Uso: $0 [comando]"
    echo -e ""
    echo -e "Comandos disponíveis:"
    echo -e "  ping          - Testa conexão"
    echo -e "  info          - Mostra informações do servidor"
    echo -e "  stats         - Mostra estatísticas"
    echo -e "  keys [pattern] - Lista chaves (padrão: compozy:*)"
    echo -e "  monitor       - Monitora comandos em tempo real"
    echo -e "  cli           - Abre redis-cli interativo"
    echo -e ""
    echo -e "Exemplos:"
    echo -e "  $0 ping"
    echo -e "  $0 info"
    echo -e "  $0 keys 'compozy:*'"
    echo -e "  $0 monitor"
    exit 0
fi

COMMAND="$1"

case "$COMMAND" in
    ping)
        echo -e "${GREEN}Testando conexão...${NC}"
        run_redis_command "PING"
        ;;
    info)
        echo -e "${GREEN}Informações do servidor Redis:${NC}\n"
        run_redis_command "INFO"
        ;;
    stats)
        echo -e "${GREEN}Estatísticas do Redis:${NC}\n"
        run_redis_command "INFO stats"
        ;;
    keys)
        PATTERN="${2:-compozy:*}"
        echo -e "${GREEN}Chaves Redis (padrão: $PATTERN):${NC}\n"
        run_redis_command "KEYS $PATTERN"
        ;;
    monitor)
        echo -e "${GREEN}Monitorando comandos Redis (Ctrl+C para sair)...${NC}\n"
        run_redis_command "MONITOR"
        ;;
    cli)
        echo -e "${GREEN}Abrindo redis-cli interativo...${NC}"
        if [ "$USE_DOCKER" = true ]; then
            if command -v docker-compose &> /dev/null; then
                docker-compose exec redis redis-cli
            else
                docker compose exec redis redis-cli
            fi
        else
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT"
        fi
        ;;
    *)
        echo -e "${RED}Comando desconhecido: $COMMAND${NC}"
        echo -e "Execute '$0' sem argumentos para ver os comandos disponíveis"
        exit 1
        ;;
esac
