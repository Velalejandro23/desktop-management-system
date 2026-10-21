from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database.db import Base

class Visita(Base):
    __tablename__ = "visitas"

    id = Column(Integer, primary_key=True)
    titulo = Column(String(150))
    descripcion = Column(String)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    recibe_persona = Column(String(100))
    direccion = Column(String(255))
    tipo_visita = Column(String(100))
    objetivo = Column(String)
    persona_hace_visita = Column(String(100))
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    estado = Column(String(50))
