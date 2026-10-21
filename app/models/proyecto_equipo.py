from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database.db import Base

class ProyectoEquipo(Base):
    __tablename__ = "proyecto_equipos"

    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"))
    equipo_id = Column(Integer, ForeignKey("equipos.id", ondelete="CASCADE"))
    cantidad = Column(Integer, default=1) # New field to track quantity

    proyecto = relationship("Proyecto", back_populates="equipos_asignados")
    equipo = relationship("Equipo", back_populates="proyectos_asignados")
