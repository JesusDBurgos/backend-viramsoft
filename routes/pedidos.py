from fastapi import APIRouter, Depends,status, Response, HTTPException
from config.database import conn,get_db,database
from models.index import Pedido_table,DetallePedido_table, Producto_table
from schemas.index import PedidoAggPydantic,ProductoPydantic, ProductosPedAggPydantic 
from sqlalchemy.orm import Session
from sqlalchemy import select,update
from datetime import datetime
from itertools import count
from typing import List

pedidosR = APIRouter()


@pedidosR.get("/order",summary="Este endpoint consulta los pedidos", status_code=status.HTTP_200_OK,tags=["Pedido"])
def get_orders(db: Session = Depends(get_db)):
    """
    Obtiene todos los pedidos desde la base de datos.

    Args:
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con la lista de pedidos.
    """
    # Consultar todos los productos de la base de datos utilizando SQLAlchemy
    orders = db.query(Pedido_table).all()
    # Verificar si hay productos. Si no hay productos, lanzar una excepción 404 (Not Found)
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron pedidos")
    # Devolver una respuesta JSON con la lista de productos obtenidos
    return {"pedidos": orders}

async def create_order(pedido: PedidoAggPydantic, productos: List[ProductosPedAggPydantic] = None):
    async with database.transaction():
        # Insertar el pedido en la tabla de pedidos utilizando SQLAlchemy
        db_pedido = Pedido_table(
            documentoCliente=pedido.documentoCliente,
            observacion=pedido.observacion,
            fechaEntrega=pedido.fechaEntrega,
            valorTotal=0,
            estado="Pendiente",
        )
        async with database.transaction():
            await database.execute(Pedido_table.__table__.insert().values(db_pedido))
            # Obtén el ID del pedido recién insertado
            last_record = await database.fetch_one("SELECT LAST_INSERT_ID()")
            id_pedido = last_record["LAST_INSERT_ID()"]

        valorTotalPed = 0.0
        id_detalle_counter = count(start=1)

        for producto in productos:
            # Verificar si el producto existe en la base de datos
            existing_product = await database.fetch_one(
                "SELECT * FROM Producto_table WHERE idProducto = :idProducto",
                values={"idProducto": producto.idProducto},
            )
            if not existing_product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe")

            valorVenta = existing_product["valorVenta"] * producto.cantidad
            valorTotalPed += valorVenta

            id_detalle = next(id_detalle_counter)

            await database.execute(
                DetallePedido_table.__table__.insert().values(
                    idDetalle=id_detalle,
                    idPedido=id_pedido,
                    idProducto=producto.idProducto,
                    cantidad=producto.cantidad,
                    precio=valorVenta,
                )
            )

        # Actualizar el valor total del pedido
        await database.execute(
            Pedido_table.__table__.update().values(valorTotal=valorTotalPed).where(Pedido_table.idPedido == id_pedido)
        )

    return Response(status_code=status.HTTP_201_CREATED, content="Pedido creado exitosamente")
   ## return {"message": "Pedido creado exitosamente"}