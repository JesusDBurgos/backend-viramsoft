from fastapi import APIRouter, Depends,status, Response, HTTPException
from config.database import conn,get_db
from models.index import Pedido_table,DetallePedido_table, Producto_table
from schemas.index import PedidoAggPydantic,ProductoPydantic, CantidadPydantic, ProductosIdPydantic
from sqlalchemy.orm import Session
from sqlalchemy import select,update
from datetime import datetime
from typing import List

pedidosR = APIRouter()
#fecha - 


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
def create_order(pedido: PedidoAggPydantic, id: List[ProductosIdPydantic],
                 db: Session = Depends(get_db), cantidadI: List[CantidadPydantic] = None):
    # Obtener la fecha actual
    fecha_actual = datetime.now()
    fecha_pedido = fecha_actual.strftime("%Y-%m-%d")
    db_pedido = Pedido_table(
                              documentoCliente = pedido.documentoCliente,
                              observacion = pedido.observacion,
                              fechaPedido= fecha_pedido,
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
    for id,cantidad in zip(id,cantidadI):
        producto_accedido = conn.execute(select(Producto_table).where(Producto_table.idProducto == id.id)).fetchone()
        producto_accedido = producto_accedido._asdict()
        producto_accedido['idProducto'] = str(producto_accedido['idProducto'])
        producto_pydantic = ProductoPydantic(**producto_accedido)
        valorVenta = producto_pydantic.valorVenta * cantidad.cantidad
        valorTotalPed += valorVenta
        db_productos = DetallePedido_table(
                                            idDetalle = db_pedido.idPedido,
                                            idPedido = db_pedido.idPedido,
                                            idProducto = producto_pydantic.idProducto,
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