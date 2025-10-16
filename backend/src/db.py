# backend/src/db.py

import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base


def _build_url_from_parts() -> str | None:
    """
    Monta a URL do Postgres a partir das variáveis:
      DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    Retorna None se faltar algum campo essencial.
    """
    host = os.getenv("DB_HOST")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    pwd  = os.getenv("DB_PASSWORD")
    port = os.getenv("DB_PORT", "5432")

    if not all([host, name, user, pwd]):
        return None

    # Escapa user/senha para caracteres especiais
    user_q = quote_plus(user)
    pwd_q  = quote_plus(pwd)

    # Usa psycopg (v3)
    return f"postgresql+psycopg://{user_q}:{pwd_q}@{host}:{port}/{name}"


# 1) Pega DATABASE_URL se já existir
DATABASE_URL = os.getenv("DATABASE_URL")

# 2) Se não existir, tenta montar a partir de DB_*
if not DATABASE_URL:
    DATABASE_URL = _build_url_from_parts()

# 3) Se vier com 'postgresql://' troca para 'postgresql+psycopg://'
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# 4) Schema (opcional). No Postgres, definimos via search_path.
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA")

connect_args = {}
if DATABASE_SCHEMA:
    # Define o search_path no Postgres para criar/usar tabelas nesse schema
    connect_args["options"] = f"-csearch_path={DATABASE_SCHEMA}"

# 5) Fallback local (dev) para SQLite, se nada de Postgres foi informado
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///db.sqlite3"
    connect_args = {}  # SQLite não usa essas opções

# 6) Cria o engine
engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,   # evita conexões quebradas
    pool_recycle=1800,    # recicla conexões a cada 30 min
)

# 7) Session/Base
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
)
Base = declarative_base()
