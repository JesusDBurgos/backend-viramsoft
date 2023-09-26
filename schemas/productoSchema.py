from datetime import date
from fastapi import UploadFile,File
from typing import Optional
from pydantic import BaseModel

class ProductoPydantic(BaseModel):
    nombre: str = "Varsol"
    marca: str = "P&G"
    categoria: str = "Líquidos"
    cantidad: int = "15"
    valorCompra: int = "4200"
    valorVenta: int = "6500"
    unidadMedida: str = "500ML"
    imagen: UploadFile = None


class ProductoUpdatePydantic(BaseModel):
    cantidad: int = "15"
    valorCompra: int = "4200"
    valorVenta: int = "6500"
    
class CantidadPydantic(BaseModel):
    cantidad: int

class ProductosPedAggPydantic(BaseModel):
    idProducto: int
    cantidad: int

class ProductosIdPydantic(BaseModel):
    producto_id: int

class ProductosCatPydantic(BaseModel):
    categoria: str
