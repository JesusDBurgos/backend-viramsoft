from pydantic import BaseModel

class detallePedPydantic(BaseModel):
    idDetalle: int = "1"
    idPedido: int = "1"
    idProducto: int = "3"
    cantidad: int = "4"
    precio: float = "100"
