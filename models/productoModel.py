from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import String, Integer, Float, Date
from models.base import Base

## Los id son Integer en la base de datos pero en el modelo pydantic String 
class Producto_table(Base): 
    __tablename__ = "producto"
    idProducto = Column(Integer,autoincrement=True, primary_key=True, nullable=False)
    nombre = Column(String(255),nullable=False)
    marca = Column(String(255), nullable=False)
    categoria = Column(String(255), nullable=False)
    cantidad = Column(Integer,nullable=False)
    valorCompra = Column(Integer,nullable=False)
    valorVenta = Column(Integer,nullable=False)
    unidadMedida = Column(String(255),nullable=False)


#Base.metadata.create_all(engine)

