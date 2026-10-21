from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database.db import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    rol = Column(String(20), default="operador")
    estado = Column(Integer, default=1)
    fecha_creacion = Column(DateTime, default=datetime.now)
