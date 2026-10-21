from app.models.db import SessionLocal
from app.models.usuario import Usuario
from app.utils.security import hash_password

def crear_admin():
    session = SessionLocal()

    # Verificar si ya existe un admin
    existe = session.query(Usuario).filter_by(usuario="admin").first()
    if existe:
        print("⚠️ El usuario admin ya existe.")
        return

    admin = Usuario(
        usuario="admin",
        password=hash_password("admin123"),
        rol="admin",
        estado=1
    )

    session.add(admin)
    session.commit()
    session.close()

    print("✅ Usuario administrador creado correctamente.")
    print("Usuario: admin")
    print("Contraseña: admin123")

if __name__ == "__main__":
    crear_admin()
