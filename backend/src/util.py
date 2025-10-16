# util.py — usar PBKDF2 (compatível no Windows) em vez de bcrypt
from passlib.hash import pbkdf2_sha256

def hash_password(p: str) -> str:
    return pbkdf2_sha256.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pbkdf2_sha256.verify(p, hashed)
