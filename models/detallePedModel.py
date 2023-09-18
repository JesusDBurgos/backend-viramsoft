from sqlalchemy import Column,ForeignKey,PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer, Float
from models.base import Base

class DetallePedido_table(Base):
    __tablename__ = "detallePedido"
    idPedido = Column(Integer, ForeignKey("pedido.idPedido"),primary_key=True, nullable=False )
    idProducto = Column( Integer, ForeignKey("producto.idProducto"), primary_key=True, nullable=False)
    cantidad = Column( Integer, nullable=False)
    precio = Column(Float, nullable=False)

    pedido = relationship("Pedido_table", back_populates="detalles")
    producto = relationship("Producto_table", back_populates="detalles")

    __table_args__ = (PrimaryKeyConstraint('idPedido', 'idProducto'),)