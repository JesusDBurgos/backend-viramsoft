from fastapi import APIRouter, Depends,status, Response, HTTPException
from config.database import conn,get_db
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

@pedidosR.post("/create_order",summary="Este endpoint crea un pedido",status_code=status.HTTP_201_CREATED,tags=["Pedido"])
def create_order(pedido: PedidoAggPydantic, productos: List[ProductosPedAggPydantic] = None,
                 db: Session = Depends(get_db)):
    # Obtener la fecha actual
    fecha_actual = datetime.now()
    fecha_pedido = fecha_actual.strftime("%Y-%m-%d")
    fecha_entrega_str = pedido.fechaEntrega.strftime("%Y-%m-%d")
    db_pedido = Pedido_table(
                              documentoCliente = pedido.documentoCliente,
                              observacion = pedido.observacion,
                              fechaPedido= fecha_pedido,
                              fechaEntrega= fecha_entrega_str,
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
    # Inicializar un contador para generar idDetalle únicos
    ##id_detalle_counter = count(start=0)
    for producto in productos:
        # Verificar si el producto existe en la base de datos
        existing_product = db.query(Producto_table).filter(Producto_table.idProducto == producto.idProducto).first()
        if not existing_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe")
        producto_accedido = existing_product 
        producto_accedido.idProducto = str(producto_accedido.idProducto)
        producto_pydantic = ProductoPydantic(**producto_accedido.__dict__)
        valorVenta = producto_pydantic.valorVenta * producto.cantidad
        valorTotalPed += valorVenta
        # Generar un nuevo idDetalle único utilizando el contador
        db_productos = DetallePedido_table(
                                            idPedido = db_pedido.idPedido,
                                            idProducto = producto_accedido.idProducto,
                                            cantidad = producto.cantidad,
                                            precio = valorVenta
                                        )
        # Agregar el detalle del pedido a la sesión y confirmar cambios
        db.add(db_productos)
    # Actualiza el valor total del pedido
    db_pedido.valorTotal = valorTotalPed
    # Realiza el commit de los cambios en la sesión
    db.commit()

    return Response(status_code=status.HTTP_201_CREATED, content="Pedido creado exitosamente")