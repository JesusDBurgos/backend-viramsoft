from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import String, Integer, Float, Date
from models.base import Base

## Los id son Integer en la base de datos pero en el modelo pydanticString 
class Producto_table(Base): 
    __tablename__ = "producto"
    idProducto = Column(Integer,autoincrement=True, primary_key=True, nullable=False)
    nombre = Column(String(255),nullable=False)
    cantidad = Column(Integer,nullable=False)
    valorCompra = Column(Float,nullable=False)
    valorVenta = Column(Float,nullable=False)
    unidadMedida = Column(String(255),nullable=False)
    fechaVencimiento = Column(Date)


#Base.metadata.create_all(engine)

