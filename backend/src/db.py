import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def _build_database_url():
    # Preferir DATABASE_URL completa
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # Fallback por partes
    user = os.getenv("DB_USER", "")
    pwd = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "postgres")
    sslmode = os.getenv("DB_SSLMODE", "disable")
    schema = os.getenv("DB_SCHEMA", None)

    # Escapa '@' etc. se vierem sem estar encodados
    from urllib.parse import quote
    pwd_enc = pwd if "%" in pwd else quote(pwd, safe="")

    url = f"postgresql+psycopg://{user}:{pwd_enc}@{host}:{port}/{name}?sslmode={sslmode}"
    if schema:
        from urllib.parse import urlencode, parse_qsl, urlsplit, urlunsplit, quote_plus
        scheme, netloc, path, query, frag = urlsplit(url)
        q = dict(parse_qsl(query))
        q["options"] = f"-csearch_path={schema}"
        query = urlencode(q, doseq=True, quote_via=quote_plus)
        url = urlunsplit((scheme, netloc, path, query, frag))

    return url

DATABASE_URL = _build_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
