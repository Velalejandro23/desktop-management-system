from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database.db import Base

class Gasto(Base):
    __tablename__ = "gastos"

    id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    descripcion = Column(String, nullable=False)
    cantidad = Column(Float, nullable=False)
    fecha = Column(Date, nullable=False) # Added fecha column

    proyecto = relationship("Proyecto", back_populates="gastos_registrados")