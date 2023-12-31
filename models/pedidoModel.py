from sqlalchemy import Column,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import String, Integer, Float, Date
from models.base import Base

class Pedido_table(Base):
    __tablename__ = "pedido"
    idPedido = Column( Integer,primary_key=True, autoincrement=True, nullable=False)
    documentoCliente = Column(String(255), ForeignKey("cliente.documento"), nullable=False)
    idVendedor = Column(Integer, ForeignKey("usuario.id"),nullable=False)
    observacion = Column(String(255), nullable=True)
    fechaPedido = Column(Date, nullable=False)
    fechaEntrega = Column(Date,nullable=False )
    valorTotal = Column(Float, nullable=False)
    estado = Column(String(255), nullable=False)
    
    detalles = relationship("DetallePedido_table", back_populates="pedido")
    clientes = relationship("Cliente_table", back_populates="pedido")
    usuarios = relationship("User", back_populates="pedido")
