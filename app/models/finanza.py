from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from app.database.db import Base

class Finanza(Base):
    __tablename__ = "finanzas"

    id = Column(Integer, primary_key=True)
    tipo = Column(String(20))  # ingreso / egreso
    concepto = Column(String(150))
    monto = Column(Float)
    fecha = Column(Date)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
