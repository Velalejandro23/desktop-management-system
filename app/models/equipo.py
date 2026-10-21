from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship # Import relationship
from app.database.db import Base

class Equipo(Base):
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    cantidad = Column(Integer)
    estado = Column(String(50))
    valor_unitario = Column(Float)
    observaciones = Column(String)
    imagen = Column(String)  # Nuevo campo para la ruta de la imagen del equipo

    # Relationships
    proyectos_asignados = relationship("ProyectoEquipo", back_populates="equipo")

