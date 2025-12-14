# Configuração do Ambiente de Desenvolvimento

## Pré-requisitos

### 1. PostgreSQL

```bash
# Instalar
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# Criar usuário e banco
sudo -u postgres psql -c "CREATE USER compozy WITH PASSWORD 'compozy_password' CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE compozy OWNER compozy;"

# Verificar
sudo -u postgres psql -c "\l" | grep compozy
```

### 2. Redis

```bash
# Instalar
sudo apt-get install -y redis-server

# Iniciar
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verificar
redis-cli ping  # Deve retornar PONG
```

### 3. Python 3.11+

```bash
python3 --version  # Deve ser 3.11 ou superior
```

## Setup do Projeto

```bash
# 1. Clonar e entrar no projeto
cd ~/compozy_project

# 2. Criar e ativar virtualenv
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar ambiente
cp .env.example .env
# Edite .env se necessário

# 5. Verificar e migrar
python manage.py setup
```

## Uso Diário

```bash
# Ativar ambiente e rodar servidor
cd ~/compozy_project
source venv/bin/activate
python manage.py runserver
```

Acesse: http://localhost:8000

## Comandos Úteis

```bash
# Verificar conexões
python manage.py setup --check

# Criar migrações após mudar models
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Shell Django
python manage.py shell
```

## Celery (para tarefas assíncronas)

```bash
# Em outro terminal
source venv/bin/activate
celery -A config worker -l info
```

## Problemas Comuns

### PostgreSQL não conecta
```bash
# Verificar se está rodando
sudo systemctl status postgresql

# Reiniciar
sudo systemctl restart postgresql
```

### Redis não conecta
```bash
# Verificar se está rodando
sudo systemctl status redis-server

# Reiniciar
sudo systemctl restart redis-server
```

### Permissão negada no banco
```bash
sudo -u postgres psql -c "ALTER USER compozy CREATEDB;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE compozy TO compozy;"
```
