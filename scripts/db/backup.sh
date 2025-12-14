#!/bin/bash
# Script para fazer backup do banco de dados PostgreSQL
# Suporta Docker e instalação local

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
BACKUP_DIR=${BACKUP_DIR:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/compozy_backup_${TIMESTAMP}.sql"

# Criar diretório de backups se não existir
mkdir -p "$BACKUP_DIR"

echo -e "${GREEN}=== Backup do Banco de Dados Compozy ===${NC}\n"

# Verificar se está usando Docker
USE_DOCKER=false
if command -v docker &> /dev/null || command -v docker-compose &> /dev/null; then
    if command -v docker-compose &> /dev/null; then
        if docker-compose ps db 2>/dev/null | grep -q "Up"; then
            USE_DOCKER=true
            CONTAINER_NAME=$(docker-compose ps -q db)
        fi
    elif command -v docker &> /dev/null; then
        if docker compose ps db 2>/dev/null | grep -q "Up"; then
            USE_DOCKER=true
            CONTAINER_NAME=$(docker compose ps -q db)
        fi
    fi
fi

if [ "$USE_DOCKER" = true ]; then
    echo -e "${GREEN}Usando Docker para backup...${NC}"
    
    # Fazer backup via Docker
    if command -v docker-compose &> /dev/null; then
        docker-compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"
    else
        docker compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Backup criado com sucesso: ${BACKUP_FILE}${NC}"
        
        # Comprimir backup
        echo -e "${YELLOW}Comprimindo backup...${NC}"
        gzip -f "$BACKUP_FILE"
        echo -e "${GREEN}Backup comprimido: ${BACKUP_FILE}.gz${NC}"
    else
        echo -e "${RED}Erro ao criar backup!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Usando instalação local para backup...${NC}"
    
    # Verificar se pg_dump está disponível
    if ! command -v pg_dump &> /dev/null; then
        echo -e "${RED}Erro: pg_dump não encontrado!${NC}"
        echo -e "Instale PostgreSQL client tools"
        exit 1
    fi
    
    # Solicitar senha se necessário
    export PGPASSWORD="${DB_PASSWORD:-compozy_dev_password}"
    
    # Fazer backup
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -F p > "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Backup criado com sucesso: ${BACKUP_FILE}${NC}"
        
        # Comprimir backup
        echo -e "${YELLOW}Comprimindo backup...${NC}"
        gzip -f "$BACKUP_FILE"
        echo -e "${GREEN}Backup comprimido: ${BACKUP_FILE}.gz${NC}"
    else
        echo -e "${RED}Erro ao criar backup!${NC}"
        exit 1
    fi
fi

# Mostrar tamanho do backup
if [ -f "${BACKUP_FILE}.gz" ]; then
    SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    echo -e "\n${GREEN}Tamanho do backup: ${SIZE}${NC}"
fi

echo -e "\n${GREEN}=== Backup concluído! ===${NC}"
