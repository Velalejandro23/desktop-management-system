from app.models.db import SessionLocal
from app.models.usuario import Usuario
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def autenticar(usuario, password):
    db = SessionLocal()

    password_hash = hash_password(password)

    user = db.query(Usuario).filter(
        Usuario.usuario == usuario,
        Usuario.password == password_hash,
        Usuario.estado == 1
    ).first()

    db.close()
    return user
