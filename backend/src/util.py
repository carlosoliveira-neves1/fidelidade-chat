import bcrypt
import hmac

BCRYPT_ROUNDS = 12  # custo padrão

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    try:
        ok = bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        # garante comparação constante de um byte para evitar timing nuance
        return hmac.compare_digest(b"\x01" if ok else b"\x00", b"\x01")
    except Exception:
        return False
