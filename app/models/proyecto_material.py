from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship # Import relationship
from app.database.db import Base

class ProyectoMaterial(Base):
    __tablename__ = "proyecto_materiales"

    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"))
    material_id = Column(Integer, ForeignKey("materiales.id", ondelete="CASCADE"))
    cantidad = Column(Float)
    costo = Column(Float)

    proyecto = relationship("Proyecto", back_populates="materiales_asignados")
    material = relationship("Material", overlaps="proyectos_asignados") # Add relationship to Material

