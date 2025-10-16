import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# -----------------------------
# Preferência: usar DB_* e montar a URL
# (Se DATABASE_URL estiver setado, ele será usado diretamente)
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_USER = os.getenv("DB_USER", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "")

    if DB_HOST and DB_NAME and DB_USER:
        # psycopg3 driver
        # sslmode=require é comum em provedores; se sua instância não exigir, pode remover.
        DATABASE_URL = (
            f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
        )
    else:
        # Fallback local (para dev) — NÃO usado no Render
        DATABASE_URL = "sqlite:///db.sqlite3"

# Schema para o Postgres
DATABASE_SCHEMA = os.getenv("DB_SCHEMA") or os.getenv("DATABASE_SCHEMA") or ""

connect_args = {}
if DATABASE_SCHEMA:
    # Define o search_path para criar/usar as tabelas no schema desejado
    connect_args["options"] = f"-csearch_path={DATABASE_SCHEMA}"

# Engine
engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)

# Session
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
)

# Base
Base = declarative_base()
