from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base
from datetime import datetime

class IngresoProyecto(Base):
    __tablename__ = "ingresos_proyecto"

    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    descripcion = Column(String, nullable=False)
    cantidad = Column(Float, nullable=False)
    fecha = Column(Date, nullable=False, default=datetime.now) # Default to current date

    proyecto = relationship("Proyecto", back_populates="ingresos_registrados")
