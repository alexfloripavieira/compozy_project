#!/bin/bash
# Script para configurar PostgreSQL 16 para o projeto Compozy
# Suporta instalação via Docker ou local

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Configuração do PostgreSQL para Compozy ===${NC}\n"

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
    echo -e "\n${GREEN}Usando Docker para PostgreSQL...${NC}"
    
    # Verificar se docker-compose.yml existe
    if [ ! -f "docker-compose.yml" ]; then
        echo -e "${RED}Erro: docker-compose.yml não encontrado!${NC}"
        exit 1
    fi
    
    # Iniciar container do PostgreSQL
    if command -v docker-compose &> /dev/null; then
        docker-compose up -d db
    else
        docker compose up -d db
    fi
    
    echo -e "${GREEN}Aguardando PostgreSQL iniciar...${NC}"
    sleep 5
    
    # Verificar se o container está rodando
    if command -v docker-compose &> /dev/null; then
        if ! docker-compose ps db | grep -q "Up"; then
            echo -e "${RED}Erro: Container do PostgreSQL não está rodando!${NC}"
            exit 1
        fi
    else
        if ! docker compose ps db | grep -q "Up"; then
            echo -e "${RED}Erro: Container do PostgreSQL não está rodando!${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}PostgreSQL está rodando no Docker!${NC}"
    echo -e "Host: localhost"
    echo -e "Porta: 5432"
    echo -e "Database: compozy"
    echo -e "User: compozy"
    echo -e "Password: compozy_dev_password"
    
else
    echo -e "\n${YELLOW}=== Instalação Local do PostgreSQL ===${NC}"
    echo -e "Para instalar PostgreSQL 16 localmente, execute:"
    echo -e ""
    echo -e "  Ubuntu/Debian:"
    echo -e "    sudo apt update"
    echo -e "    sudo apt install postgresql-16 postgresql-contrib-16"
    echo -e ""
    echo -e "  Após instalar, execute:"
    echo -e "    sudo -u postgres createuser -s compozy"
    echo -e "    sudo -u postgres createdb -O compozy compozy"
    echo -e "    sudo -u postgres psql -c \"ALTER USER compozy WITH PASSWORD 'compozy_dev_password';\""
    echo -e ""
    echo -e "  Ou execute este script como root para configurar automaticamente:"
    echo -e "    sudo bash scripts/db/setup_postgres_local.sh"
    echo -e ""
fi

echo -e "\n${GREEN}=== Configuração concluída! ===${NC}"
