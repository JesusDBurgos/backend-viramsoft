from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
    HTTPException,
    UploadFile,
    File,
    Body,
)
from fastapi.responses import JSONResponse
from config.database import conn, get_db
from models.index import Producto_table, ImagenProducto
from schemas.index import ProductoPydantic, ProductoUpdatePydantic
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update
from typing import List
import base64
import locale
import asyncio

visualizacionesR = APIRouter()

