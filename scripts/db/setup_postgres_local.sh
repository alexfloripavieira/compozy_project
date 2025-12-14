#!/bin/bash
# Script para configurar PostgreSQL 16 localmente (requer sudo)
# Execute com: sudo bash scripts/db/setup_postgres_local.sh

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Configuração Local do PostgreSQL 16 ===${NC}\n"

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Erro: Este script precisa ser executado com sudo${NC}"
    exit 1
fi

# Verificar se PostgreSQL está instalado
if ! command -v psql &> /dev/null; then
    echo -e "${RED}PostgreSQL não está instalado!${NC}"
    echo -e "Instale com: sudo apt install postgresql-16 postgresql-contrib-16"
    exit 1
fi

# Verificar versão
PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
echo -e "${GREEN}PostgreSQL versão ${PG_VERSION} encontrado${NC}\n"

# Criar usuário compozy
echo -e "${YELLOW}Criando usuário compozy...${NC}"
sudo -u postgres psql -c "CREATE USER compozy WITH PASSWORD 'compozy_dev_password';" 2>/dev/null || \
    echo -e "${YELLOW}Usuário compozy já existe${NC}"

# Dar privilégios ao usuário
sudo -u postgres psql -c "ALTER USER compozy WITH SUPERUSER CREATEDB CREATEROLE;" 2>/dev/null || true

# Criar banco de dados
echo -e "${YELLOW}Criando banco de dados compozy...${NC}"
sudo -u postgres psql -c "CREATE DATABASE compozy OWNER compozy ENCODING 'UTF8' LC_COLLATE='pt_BR.UTF-8' LC_CTYPE='pt_BR.UTF-8' TEMPLATE template0;" 2>/dev/null || \
    echo -e "${YELLOW}Banco compozy já existe${NC}"

# Configurar timezone
echo -e "${YELLOW}Configurando timezone para America/Sao_Paulo...${NC}"
sudo -u postgres psql -d compozy -c "ALTER DATABASE compozy SET timezone = 'America/Sao_Paulo';"

# Verificar configuração
echo -e "\n${GREEN}=== Verificando configuração ===${NC}"
sudo -u postgres psql -d compozy -c "SHOW timezone;"
sudo -u postgres psql -d compozy -c "SELECT current_database(), current_user;"

echo -e "\n${GREEN}=== Configuração concluída! ===${NC}"
echo -e "Database: compozy"
echo -e "User: compozy"
echo -e "Password: compozy_dev_password"
echo -e "Timezone: America/Sao_Paulo"
