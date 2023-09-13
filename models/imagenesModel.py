from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, LargeBinary
from models.base import Base

class ImagenProducto(Base):
    __tablename__ = 'imagenes_productos'

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    imagen = Column(LargeBinary)

    # Relación con el producto
    productos = relationship('Producto', back_populates='imagenes')