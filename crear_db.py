from app.database.db import Base, engine
import app.models # This will load all models defined in app/models/__init__.py

print("DEBUG: Tables registered with Base.metadata:", Base.metadata.tables.keys())
Base.metadata.create_all(engine)

print("✅ Todas las tablas fueron creadas correctamente.")
    