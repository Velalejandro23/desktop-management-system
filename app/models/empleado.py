from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import relationship # Import relationship
from app.database.db import Base

class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    tipo_documento = Column(String(50), nullable=False)
    documento = Column(String(50), unique=True, nullable=False)
    telefono = Column(String(30))
    cargo = Column(String(50))
    tipo_contrato = Column(String(50))
    estado = Column(Integer, default=1)
    fecha_ingreso = Column(Date)
    foto = Column(String)  # ruta de la imagen

    # Relationships
    proyectos_asignados = relationship("ProyectoEmpleado") # No back_populates here, as ProyectoEmpleado handles it

