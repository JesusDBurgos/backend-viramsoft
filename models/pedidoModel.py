from sqlalchemy import Column,ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Float, Date
from models.base import Base

class Pedido_table(Base):
    __tablename__ = "pedido"
    idPedido = Column( Integer,primary_key=True, autoincrement=True, nullable=False)
    documentoCliente = Column(String(255), ForeignKey("cliente.documento"), nullable=False)
    fechaPedido = Column(Date, nullable=False)
    valorTotal = Column(Float, nullable=False)
    estado = Column(String(255), nullable=False)