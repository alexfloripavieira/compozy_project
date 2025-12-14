# 🚀 Setup Rápido do Compozy

## Comando Único de Setup

Após instalar as dependências, execute um único comando para configurar tudo:

```bash
python manage.py setup
```

Este comando irá automaticamente:

1. ✅ Iniciar PostgreSQL e Redis via Docker (se disponível)
2. ✅ Criar/atualizar o arquivo `.env` com as configurações necessárias
3. ✅ Testar conexões com PostgreSQL e Redis
4. ✅ Executar migrações do Django

## Requisitos

- Python 3.11+
- Docker (opcional, mas recomendado)
- Dependências instaladas: `pip install -r requirements.txt`

## Uso

### Primeira vez (setup completo):

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar tudo automaticamente
python manage.py setup

# 3. Rodar o servidor
python manage.py runserver
```

### Opções do comando setup:

```bash
# Pular Docker (se já tiver PostgreSQL/Redis rodando)
python manage.py setup --skip-docker

# Pular migrações
python manage.py setup --skip-migrations

# Pular ambos
python manage.py setup --skip-docker --skip-migrations
```

## O que o comando faz?

### 1. Docker
- Verifica se Docker está disponível
- Inicia `docker compose up -d db redis`
- Aguarda os serviços iniciarem

### 2. Arquivo .env
- Cria `.env` se não existir (a partir de `.env.example` ou valores padrão)
- Garante que `DATABASE_URL` está configurado
- Configura Redis e Celery

### 3. Testes de Conexão
- Testa conexão com PostgreSQL
- Testa conexão com Redis
- Mostra mensagens de erro se algo não estiver funcionando

### 4. Migrações
- Executa `makemigrations` (se necessário)
- Executa `migrate` para aplicar migrações

## Sem Docker?

Se você não tiver Docker instalado:

1. Configure PostgreSQL e Redis manualmente
2. Execute: `python manage.py setup --skip-docker`
3. Configure o `.env` manualmente com suas credenciais

## Troubleshooting

### Erro: "Docker não encontrado"
- Instale Docker ou use `--skip-docker` e configure manualmente

### Erro: "PostgreSQL não conecta"
- Verifique se o PostgreSQL está rodando
- Verifique o `DATABASE_URL` no `.env`

### Erro: "Redis não conecta"
- Verifique se o Redis está rodando
- Verifique o `REDIS_URL` no `.env`

## Próximos Passos

Após o setup:

1. Criar superusuário: `python manage.py createsuperuser`
2. Rodar servidor: `python manage.py runserver`
3. Acessar admin: http://localhost:8000/admin/
