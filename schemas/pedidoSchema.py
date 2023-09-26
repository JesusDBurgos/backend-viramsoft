from datetime import date
from typing import Optional
from pydantic import BaseModel

class PedidoPydantic(BaseModel):
    idPedido: Optional[int] = "1"
    documentoCliente: str = "12135164"
    observacion: str = " "
    fechaPedido: date = date(2023, 7, 25)
    fechaEntrega: date = date(2023,7, 30)
    valorTotal: float = "4200"
    estado: str = "Pendiente"

class PedidoAggPydantic(BaseModel):
    documentoCliente: str = "123"
    fechaEntrega: date = date(2023,7, 30)
    observacion: str = "Todo con normalidad"

class valorPedPydantic(BaseModel):
    valorTotal: float
