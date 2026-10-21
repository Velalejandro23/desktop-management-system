from sqlalchemy import Column, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship # Import relationship
from app.database.db import Base

class ProyectoEmpleado(Base):
    __tablename__ = "proyecto_empleados"

    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id", ondelete="CASCADE"))
    empleado_id = Column(Integer, ForeignKey("empleados.id", ondelete="CASCADE"))
    horas = Column(Float)
    costo = Column(Float)

    proyecto = relationship("Proyecto", back_populates="empleados_asignados")
    empleado = relationship("Empleado", overlaps="proyectos_asignados") # Add relationship to Empleado

