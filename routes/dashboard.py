from fastapi import APIRouter, Depends,status, Response, HTTPException
from config.database import conn,get_db
from models.index import Pedido_table,DetallePedido_table, Producto_table, Cliente_table
from schemas.index import PedidoAggPydantic,ProductoPydantic, ProductosPedAggPydantic 
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select,update, text
from datetime import datetime
from itertools import count
from typing import List

dashboardR = APIRouter()