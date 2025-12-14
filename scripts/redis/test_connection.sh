#!/bin/bash
# Script para testar conexão com o Redis

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

echo -e "${GREEN}=== Teste de Conexão Redis ===${NC}\n"

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

if [ "$USE_DOCKER" = true ]; then
    echo -e "${GREEN}Testando conexão via Docker...${NC}\n"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose exec -T redis redis-cli ping > /dev/null 2>&1
    else
        docker compose exec -T redis redis-cli ping > /dev/null 2>&1
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Conexão bem-sucedida!${NC}\n"
        
        # Mostrar informações do Redis
        if command -v docker-compose &> /dev/null; then
            docker-compose exec -T redis redis-cli INFO server | grep -E "redis_version|os|process_id"
            echo ""
            docker-compose exec -T redis redis-cli INFO stats | grep -E "total_connections_received|total_commands_processed"
        else
            docker compose exec -T redis redis-cli INFO server | grep -E "redis_version|os|process_id"
            echo ""
            docker compose exec -T redis redis-cli INFO stats | grep -E "total_connections_received|total_commands_processed"
        fi
    else
        echo -e "${RED}✗ Erro ao conectar ao Redis!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Testando conexão local...${NC}\n"
    
    # Verificar se redis-cli está disponível
    if ! command -v redis-cli &> /dev/null; then
        echo -e "${RED}Erro: redis-cli não encontrado!${NC}"
        echo -e "Instale Redis client tools ou use Docker"
        exit 1
    fi
    
    # Testar conexão
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Conexão bem-sucedida!${NC}\n"
        
        # Mostrar informações do Redis
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO server | grep -E "redis_version|os|process_id"
        echo ""
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" INFO stats | grep -E "total_connections_received|total_commands_processed"
    else
        echo -e "${RED}✗ Erro ao conectar ao Redis!${NC}"
        echo -e "Verifique se o Redis está rodando e as configurações estão corretas"
        exit 1
    fi
fi

echo -e "\n${GREEN}=== Teste concluído! ===${NC}"
