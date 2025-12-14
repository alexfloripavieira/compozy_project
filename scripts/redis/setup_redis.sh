#!/bin/bash
# Script para configurar Redis 7 para o projeto Compozy
# Suporta instalação via Docker ou local

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Configuração do Redis para Compozy ===${NC}\n"

# Verificar se Docker está disponível
if command -v docker &> /dev/null; then
    echo -e "${GREEN}Docker encontrado!${NC}"
    USE_DOCKER=true
elif command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}docker-compose encontrado!${NC}"
    USE_DOCKER=true
else
    echo -e "${YELLOW}Docker não encontrado. Usando instalação local.${NC}"
    USE_DOCKER=false
fi

if [ "$USE_DOCKER" = true ]; then
    echo -e "\n${GREEN}Usando Docker para Redis...${NC}"
    
    # Verificar se docker-compose.yml existe
    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${RED}Erro: docker-compose.yml não encontrado!${NC}"
        exit 1
    fi
    
    # Iniciar container do Redis
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d redis
    else
        docker compose up -d redis
    fi
    
    echo -e "${GREEN}Aguardando Redis iniciar...${NC}"
    sleep 3
    
    # Verificar se o container está rodando
    if command -v docker-compose &> /dev/null; then
        if ! docker-compose ps redis | grep -q "Up"; then
            echo -e "${RED}Erro: Container do Redis não está rodando!${NC}"
            exit 1
        fi
    else
        if ! docker compose ps redis | grep -q "Up"; then
            echo -e "${RED}Erro: Container do Redis não está rodando!${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}Redis está rodando no Docker!${NC}"
    echo -e "Host: localhost"
    echo -e "Porta: 6379"
    echo -e "URL: redis://127.0.0.1:6379/1"
    
else
    echo -e "\n${YELLOW}=== Instalação Local do Redis ===${NC}"
    echo -e "Para instalar Redis 7 localmente, execute:"
    echo -e ""
    echo -e "  Ubuntu/Debian:"
    echo -e "    sudo apt update"
    echo -e "    sudo apt install redis-server"
    echo -e ""
    echo -e "  macOS (Homebrew):"
    echo -e "    brew install redis"
    echo -e "    brew services start redis"
    echo -e ""
    echo -e "  Após instalar, verifique se está rodando:"
    echo -e "    redis-cli ping"
    echo -e "    (deve retornar: PONG)"
    echo -e ""
fi

echo -e "\n${GREEN}=== Configuração concluída! ===${NC}"
