from sqlalchemy import Column,ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Float, Date
from models.base import Base

class Pedido_table(Base):
    __tablename__ = "pedido"
    idPedido = Column( Integer,primary_key=True, autoincrement=True, nullable=False)
    documentoCliente = Column(String(255), ForeignKey("cliente.documento"), nullable=False)
    observacion = Column(String(255), nullable=True)
    fechaPedido = Column(Date, nullable=False)
    fechaEntrega = Column(Date,nullable=False )
    valorTotal = Column(Float, nullable=False)
    estado = Column(String(255), nullable=False)
    s
    detalles = relationship("DetallePedido_table", back_populates="pedido")
