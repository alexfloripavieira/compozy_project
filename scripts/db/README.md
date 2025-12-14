# Scripts de Configuração e Gerenciamento do PostgreSQL

Este diretório contém scripts para configurar, gerenciar e fazer backup/restore do banco de dados PostgreSQL do projeto Compozy.

## Requisitos

- PostgreSQL 16 (via Docker ou instalação local)
- Docker e Docker Compose (opcional, mas recomendado)

## Configuração Inicial

### Opção 1: Usando Docker (Recomendado)

1. Certifique-se de que o Docker está instalado e rodando
2. Execute o script de setup:
   ```bash
   ./scripts/db/setup_postgres.sh
   ```
   
   Ou inicie manualmente:
   ```bash
   docker compose up -d db
   ```

3. O banco será criado automaticamente com:
   - Database: `compozy`
   - User: `compozy`
   - Password: `compozy_dev_password`
   - Timezone: `America/Sao_Paulo`

### Opção 2: Instalação Local

1. Instale PostgreSQL 16:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install postgresql-16 postgresql-contrib-16
   ```

2. Execute o script de configuração:
   ```bash
   sudo bash scripts/db/setup_postgres_local.sh
   ```

## Configuração do .env

Adicione a seguinte linha ao seu arquivo `.env`:

```bash
DATABASE_URL=postgresql://compozy:compozy_dev_password@localhost:5432/compozy
```

## Testando a Conexão

### Via Script

```bash
./scripts/db/test_connection.sh
```

### Via Django

```bash
python manage.py dbshell
```

Dentro do shell do PostgreSQL, você pode executar:

```sql
SELECT version();
SELECT current_setting('timezone');
```

## Backup e Restore

### Fazer Backup

```bash
./scripts/db/backup.sh
```

O backup será salvo em `./backups/compozy_backup_YYYYMMDD_HHMMSS.sql.gz`

### Restaurar Backup

```bash
./scripts/db/restore.sh backups/compozy_backup_YYYYMMDD_HHMMSS.sql.gz
```

**ATENÇÃO**: A restauração irá substituir todos os dados atuais do banco!

## Configuração de Timezone

O timezone do banco de dados é configurado automaticamente para `America/Sao_Paulo` durante a inicialização.

Para verificar:

```sql
SHOW timezone;
```

Para alterar (se necessário):

```sql
ALTER DATABASE compozy SET timezone = 'America/Sao_Paulo';
```

## Scripts Disponíveis

- `setup_postgres.sh` - Configura PostgreSQL via Docker ou fornece instruções para instalação local
- `setup_postgres_local.sh` - Configura PostgreSQL localmente (requer sudo)
- `test_connection.sh` - Testa conexão com o banco de dados
- `backup.sh` - Cria backup do banco de dados
- `restore.sh` - Restaura backup do banco de dados
- `init.sql` - Script SQL executado na inicialização do container Docker

## Troubleshooting

### Erro: "Connection refused"

- Verifique se o PostgreSQL está rodando:
  ```bash
  # Docker
  docker compose ps db
  
  # Local
  sudo systemctl status postgresql
  ```

### Erro: "Authentication failed"

- Verifique as credenciais no arquivo `.env`
- Para Docker, as credenciais padrão estão em `docker-compose.yml`
- Para instalação local, verifique o usuário e senha configurados

### Erro: "Database does not exist"

- Execute o script de setup novamente:
  ```bash
  ./scripts/db/setup_postgres.sh
  ```

### Timezone incorreto

- Execute:
  ```sql
  ALTER DATABASE compozy SET timezone = 'America/Sao_Paulo';
  ```

## Variáveis de Ambiente

Os scripts podem usar as seguintes variáveis de ambiente:

- `DB_NAME` - Nome do banco (padrão: `compozy`)
- `DB_USER` - Usuário (padrão: `compozy`)
- `DB_PASSWORD` - Senha (padrão: `compozy_dev_password`)
- `DB_HOST` - Host (padrão: `localhost`)
- `DB_PORT` - Porta (padrão: `5432`)
- `BACKUP_DIR` - Diretório de backups (padrão: `./backups`)
