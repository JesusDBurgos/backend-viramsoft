from fastapi import APIRouter, Depends,status, Response
from config.database import conn,get_db
from models.index import Pedido_table,DetallePedido_table
from schemas.index import PedidoPydantic,detallePedPydantic,ProductoPydantic, CantidadPydantic
from sqlalchemy.orm import Session
from sqlalchemy import select,update
from typing import List

pedidosR = APIRouter()

# Lista para almacenar los productos recibidos en el endpoint post
lista_productos = []
lista_cantidades = []


@pedidosR.post("/create_order",summary="Este endpoint crea un producto",status_code=status.HTTP_201_CREATED,tags=["Pedido"])
def create_order(pedido: PedidoPydantic,detalle:detallePedPydantic,
                 db: Session = Depends(get_db), productos: List[ProductoPydantic] = None, cantidadI: List[CantidadPydantic] = None):
    
    db_pedido = Pedido_table(
                              documentoCliente = pedido.documentoCliente,
                              fechaPedido= pedido.fechaPedido,
                              fechaEntrega= pedido.fechaEntrega,
                              valorTotal = 0,
                              estado= "Pendiente",
                            )
    # Agregar el nuevo producto a la sesión de la base de datos
    db.add(db_pedido)
    # Confirmar los cambios en la base de datos
    db.commit()
    # Refrescar el objeto para asegurarse de que los cambios se reflejen en el objeto en memoria
    db.refresh(db_pedido)
    valorTotalPed = 0.0
    for producto,cantidad in zip(productos, cantidadI):
        valorVenta = producto.valorVenta * cantidad.cantidad
        valorTotalPed += valorVenta
        db_productos = DetallePedido_table(
                                            idDetalle = db_pedido.idPedido,
                                            idPedido = db_pedido.idPedido,
                                            idProducto = producto.idProducto,
                                            cantidad = cantidad.cantidad,
                                            precio = valorVenta
                                        )
        # Agregar el nuevo producto a la sesión de la base de datos
        db.add(db_productos)
        db.commit()
        #Refrescar el objeto para asegurarse de que los cambios se reflejen en el objeto en memoria
        db.refresh(db_productos)
        print(db_productos)
    db_pedido.valorTotal = valorTotalPed
    print(db_pedido.idPedido,valorTotalPed)
    db.commit()

    return Response(status_code=status.HTTP_201_CREATED, content="Pedido creado exitosamente")