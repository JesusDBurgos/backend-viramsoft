from datetime import date
from typing import Optional
from pydantic import BaseModel

class ProductoPydantic(BaseModel):
    idProducto: Optional[int] = 1
    nombre: str = "Varsol"
    marca: str = "P&G"
    cantidad: int = 15
    valorCompra: float = 4200
    valorVenta: float = 6500
    unidadMedida: str = "500ML"
    fechaVencimiento: date = date(2023, 7, 19)

class CantidadPydantic(BaseModel):
    cantidad: int