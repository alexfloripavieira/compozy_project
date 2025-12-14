#!/bin/bash
# Script para testar conexão com o banco de dados PostgreSQL

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configurações
DB_NAME=${DB_NAME:-compozy}
DB_USER=${DB_USER:-compozy}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_PASSWORD=${DB_PASSWORD:-compozy_dev_password}

echo -e "${GREEN}=== Teste de Conexão PostgreSQL ===${NC}\n"

# Verificar se está usando Docker
USE_DOCKER=false
if command -v docker &> /dev/null || command -v docker-compose &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        if docker-compose ps db 2>/dev/null | grep -q "Up"; then
            USE_DOCKER=true
        fi
    elif command -v docker &> /dev/null; then
        if docker compose ps db 2>/dev/null | grep -q "Up"; then
            USE_DOCKER=true
        fi
    fi
fi

if [ "$USE_DOCKER" = true ]; then
    echo -e "${GREEN}Testando conexão via Docker...${NC}\n"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1
    else
        docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Conexão bem-sucedida!${NC}\n"
        
        # Mostrar informações do banco
        if command -v docker-compose &> /dev/null; then
            docker-compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "
                SELECT 
                    current_database() as database,
                    current_user as user,
                    version() as version,
                    current_setting('timezone') as timezone;
            "
        else
            docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "
                SELECT 
                    current_database() as database,
                    current_user as user,
                    version() as version,
                    current_setting('timezone') as timezone;
            "
        fi
    else
        echo -e "${RED}✗ Erro ao conectar ao banco de dados!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Testando conexão local...${NC}\n"
    
    # Verificar se psql está disponível
    if ! command -v psql &> /dev/null; then
        echo -e "${RED}Erro: psql não encontrado!${NC}"
        echo -e "Instale PostgreSQL client tools ou use Docker"
        exit 1
    fi
    
    export PGPASSWORD="$DB_PASSWORD"
    
    # Testar conexão
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Conexão bem-sucedida!${NC}\n"
        
        # Mostrar informações do banco
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "
            SELECT 
                current_database() as database,
                current_user as user,
                version() as version,
                current_setting('timezone') as timezone;
        "
    else
        echo -e "${RED}✗ Erro ao conectar ao banco de dados!${NC}"
        echo -e "Verifique se o PostgreSQL está rodando e as credenciais estão corretas"
        exit 1
    fi
fi

echo -e "\n${GREEN}=== Teste concluído! ===${NC}"
