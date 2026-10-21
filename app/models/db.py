from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Create database path dynamically
db_path = resource_path("database/sismaep.db")
db_dir = os.path.dirname(db_path)
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

DATABASE_URL = f"sqlite:///{db_path.replace(os.sep, '/')}"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
