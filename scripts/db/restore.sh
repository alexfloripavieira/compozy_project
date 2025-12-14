#!/bin/bash
# Script para restaurar backup do banco de dados PostgreSQL
# Uso: ./restore.sh <arquivo_backup.sql.gz> ou <arquivo_backup.sql>

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo -e "${RED}Erro: Especifique o arquivo de backup${NC}"
    echo -e "Uso: $0 <arquivo_backup.sql.gz> ou <arquivo_backup.sql>"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Erro: Arquivo de backup não encontrado: ${BACKUP_FILE}${NC}"
    exit 1
fi

# Configurações
DB_NAME=${DB_NAME:-compozy}
DB_USER=${DB_USER:-compozy}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

echo -e "${GREEN}=== Restauração do Banco de Dados Compozy ===${NC}\n"
echo -e "${YELLOW}ATENÇÃO: Esta operação irá substituir todos os dados atuais!${NC}\n"

# Confirmação
read -p "Tem certeza que deseja continuar? (sim/não): " CONFIRM
if [ "$CONFIRM" != "sim" ] && [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "yes" ] && [ "$CONFIRM" != "y" ]; then
    echo -e "${YELLOW}Operação cancelada.${NC}"
    exit 0
fi

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

# Descomprimir se necessário
TEMP_FILE=""
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo -e "${YELLOW}Descomprimindo backup...${NC}"
    TEMP_FILE=$(mktemp)
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    BACKUP_FILE="$TEMP_FILE"
fi

if [ "$USE_DOCKER" = true ]; then
    echo -e "${GREEN}Usando Docker para restauração...${NC}"
    
    # Restaurar via Docker
    if command -v docker-compose &> /dev/null; then
        docker-compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"
    else
        docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Restauração concluída com sucesso!${NC}"
    else
        echo -e "${RED}Erro ao restaurar backup!${NC}"
        [ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"
        exit 1
    fi
else
    echo -e "${GREEN}Usando instalação local para restauração...${NC}"
    
    # Verificar se psql está disponível
    if ! command -v psql &> /dev/null; then
        echo -e "${RED}Erro: psql não encontrado!${NC}"
        echo -e "Instale PostgreSQL client tools"
        [ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"
        exit 1
    fi
    
    # Solicitar senha se necessário
    export PGPASSWORD="${DB_PASSWORD:-compozy_dev_password}"
    
    # Restaurar
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Restauração concluída com sucesso!${NC}"
    else
        echo -e "${RED}Erro ao restaurar backup!${NC}"
        [ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"
        exit 1
    fi
fi

# Limpar arquivo temporário
[ -n "$TEMP_FILE" ] && rm -f "$TEMP_FILE"

echo -e "\n${GREEN}=== Restauração concluída! ===${NC}"
