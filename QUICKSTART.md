# ⚡ Quick Start - Compozy

## Setup em 3 comandos

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar tudo automaticamente (Docker, .env, migrações)
python manage.py setup

# 3. Rodar o servidor
python manage.py runserver
```

Pronto! 🎉 O projeto estará rodando em http://localhost:8000

## O que o `python manage.py setup` faz?

✅ Inicia PostgreSQL e Redis via Docker  
✅ Cria/atualiza arquivo `.env`  
✅ Testa conexões  
✅ Executa migrações do Django  

## Sem Docker?

```bash
python manage.py setup --skip-docker
```

Depois configure PostgreSQL e Redis manualmente e ajuste o `.env`.

## Mais informações

Veja `README_SETUP.md` para detalhes completos.
