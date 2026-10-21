from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database.db import Base
import datetime

class Novedad(Base):
    __tablename__ = "novedades"

    id = Column(Integer, primary_key=True, index=True)
    module_name = Column(String, index=True, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    def __repr__(self):
        return f"<Novedad(id={self.id}, module_name='{self.module_name}', expires_at='{self.expires_at}')>"
