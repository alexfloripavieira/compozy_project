-- Script de inicialização do banco de dados PostgreSQL
-- Este script é executado automaticamente quando o container é criado pela primeira vez

-- Configurar timezone para America/Sao_Paulo
SET timezone = 'America/Sao_Paulo';

-- Criar extensões úteis (se necessário)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Configurações adicionais do banco
ALTER DATABASE compozy SET timezone = 'America/Sao_Paulo';
ALTER DATABASE compozy SET lc_collate = 'pt_BR.UTF-8';
ALTER DATABASE compozy SET lc_ctype = 'pt_BR.UTF-8';

-- Log de sucesso
DO $$
BEGIN
    RAISE NOTICE 'Banco de dados compozy inicializado com sucesso!';
    RAISE NOTICE 'Timezone configurado para: America/Sao_Paulo';
END $$;
