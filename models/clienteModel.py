from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import String
from models.base import Base

class Cliente_table(Base):
    __tablename__ = "cliente"
    documento = Column( String(255), nullable=False, primary_key=True, unique=True)
    nombre = Column( String(255), nullable=False)
    apellido = Column( String(255), nullable=False)
    direccion = Column( String(255), nullable=False)
    telefono = Column( String(255), nullable=False)