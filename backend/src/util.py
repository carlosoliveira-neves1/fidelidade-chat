# backend/src/util.py
import bcrypt

_SALT_ROUNDS = 12  # use 12–14 em produção

def hash_password(plain: str) -> str:
    if not isinstance(plain, str):
        raise TypeError("plain must be a string")
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(_SALT_ROUNDS))
    return hashed.decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False
