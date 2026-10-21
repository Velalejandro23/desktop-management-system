from sqlalchemy import Column, Integer, String, Float, Date, Text
from sqlalchemy.orm import relationship # Import relationship
from app.database.db import Base

class Proyecto(Base):
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False, unique=True)
    cliente = Column(String(150))
    descripcion = Column(Text)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    estado = Column(String(50))
    presupuesto = Column(Float)
    anticipo = Column(Float)
    costo_total = Column(Float)

    # Relationships
    empleados_asignados = relationship("ProyectoEmpleado", back_populates="proyecto")
    materiales_asignados = relationship("ProyectoMaterial", back_populates="proyecto")
    equipos_asignados = relationship("ProyectoEquipo", back_populates="proyecto")
    gastos_registrados = relationship("Gasto", back_populates="proyecto") # New relationship for expenses
    ingresos_registrados = relationship("IngresoProyecto", back_populates="proyecto") # New relationship for project incomes

