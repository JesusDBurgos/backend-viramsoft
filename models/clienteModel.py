from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String, Date
from datetime import datetime
from models.base import Base

class Cliente_table(Base):
    __tablename__ = "cliente"
    documento = Column( String(255), nullable=False, primary_key=True, unique=True)
    nombre = Column( String(255), nullable=False)
    direccion = Column( String(255), nullable=False)
    telefono = Column( String(255), nullable=False)
    estado = Column(String(255), nullable=False)
    fecha_agregado = Column(Date, nullable=False)

    pedido = relationship("Pedido_table", back_populates="clientes")