from datetime import date
from typing import Optional
from pydantic import BaseModel

class ProductoPydantic(BaseModel):
    idProducto: Optional[int] = 1
    nombre: str = "Varsol"
    marca: str = "P&G"
    categoria: str = "Líquidos"
    cantidad: int = 15
    valorCompra: int = 4200
    valorVenta: int = 6500
    unidadMedida: str = "500ML"
    fechaVencimiento: date = date(2023, 7, 19)

class ProductoUpdatePydantic(BaseModel):
    nombre: str = "Varsol"
    marca: str = "P&G"
    cantidad: int = 15
    valorCompra: int = 4200
    valorVenta: int = 6500
    unidadMedida: str = "500ML"
    fechaVencimiento: date = date(2023, 7, 19)

class CantidadPydantic(BaseModel):
    cantidad: int

class ProductosIdPydantic(BaseModel):
    id: int

class ProductosCatPydantic(BaseModel):
    categoria: str
