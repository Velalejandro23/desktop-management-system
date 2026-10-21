from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship # Import relationship
from app.database.db import Base

class Material(Base):
    __tablename__ = "materiales"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    categoria = Column(String(50))
    unidad = Column(String(20))
    cantidad = Column(Integer, default=0) # Nuevo campo para la cantidad
    marca = Column(String(50)) # Nuevo campo para la marca del material
    imagen = Column(String)  # Nuevo campo para la ruta de la imagen del material

    # Relationships
    proyectos_asignados = relationship("ProyectoMaterial") # No back_populates here, as ProyectoMaterial handles it

