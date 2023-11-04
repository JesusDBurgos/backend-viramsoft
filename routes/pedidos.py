from fastapi import APIRouter, Depends,status, Response, HTTPException
from config.database import conn,get_db
from models.index import Pedido_table,DetallePedido_table, Producto_table, Cliente_table,User
from auth.jwt import decode_token
from schemas.index import PedidoAggPydantic,ProductoPydantic, ProductosPedAggPydantic 
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select,update, text
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
    orders = db.query(Pedido_table).join(Cliente_table).options(joinedload(Pedido_table.clientes)).all()
    # Verificar si hay productos. Si no hay productos, lanzar una excepción 404 (Not Found)
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron pedidos")
    
    # Crear una lista para almacenar los pedidos formateados
    formatted_orders = []
    # Recorrer la lista de pedidos y construir el diccionario de respuesta
    for order in orders:
        order_dict = {
            "documentoCliente": order.clientes.documento,  # Obtener el documento del cliente
            "vendedor": order.vendedor,
            "observacion": order.observacion,
            "fechaEntrega": str(order.fechaEntrega),
            "estado": order.estado,
            "idPedido": order.idPedido,
            "fechaPedido": str(order.fechaPedido),
            "valorTotal": order.valorTotal,
            "telefono": order.clientes.telefono,  # Obtener el teléfono del cliente
            "nombre": order.clientes.nombre,  # Obtener el nombre del cliente
            "direccion": order.clientes.direccion  # Obtener la dirección del cliente
        }
        formatted_orders.append(order_dict)

    # Devolver una respuesta JSON con la lista de pedidos formateados
    return {"pedidos": formatted_orders}

@pedidosR.get("/order_by_vendor",summary="Este endpoint consulta los pedidos", status_code=status.HTTP_200_OK,tags=["Pedido"])
def get_orders_by_vendor(token: str,db: Session = Depends(get_db)):
    """
    Obtiene todos los pedidos desde la base de datos.

    Args:
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con la lista de pedidos.
    """
    vendedor = decode_token(token)
    # Consultar todos los productos de la base de datos utilizando SQLAlchemy
    orders = db.query(Pedido_table).join(Cliente_table).options(joinedload(Pedido_table.clientes)).filter(Pedido_table.idVendedor == vendedor["id"]).all()
    # Verificar si hay productos. Si no hay productos, lanzar una excepción 404 (Not Found)
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron pedidos")
    
    vendedor_nombre = db.query(User).filter(User.id == vendedor["id"]).first()
    # Crear una lista para almacenar los pedidos formateados
    formatted_orders = []
    # Recorrer la lista de pedidos y construir el diccionario de respuesta
    for order in orders:
        order_dict = {
            "documentoCliente": order.clientes.documento,  # Obtener el documento del cliente
            "vendedor": vendedor_nombre.nombre,
            "observacion": order.observacion,
            "fechaEntrega": str(order.fechaEntrega),
            "estado": order.estado,
            "idPedido": order.idPedido,
            "fechaPedido": str(order.fechaPedido),
            "valorTotal": order.valorTotal,
            "telefono": order.clientes.telefono,  # Obtener el teléfono del cliente
            "nombre": order.clientes.nombre,  # Obtener el nombre del cliente
            "direccion": order.clientes.direccion  # Obtener la dirección del cliente
        }
        formatted_orders.append(order_dict)

    # Devolver una respuesta JSON con la lista de pedidos formateados
    return {"pedidos": formatted_orders}

@pedidosR.get("/detalle_pedido/{pedido_id}", status_code=status.HTTP_200_OK, summary="Consulta el detalle de un pedido", tags=["Pedido"])
def get_detalle_pedido(pedido_id: int, db: Session = Depends(get_db)):
    try:        
        # Declara la consulta SQL como una expresión de texto
        consulta_sql = text(f"CALL ConsultarDetallePedido(:pedido_id)")
        
        # Llama al procedimiento almacenado utilizando SQLAlchemy
        result = db.execute(consulta_sql, {"pedido_id": pedido_id}).fetchall()
        
        if not result:
            raise HTTPException(status_code=404, detail="Detalle no encontrado")
        
        order = db.query(Pedido_table).filter(Pedido_table.idPedido == pedido_id).first()

        if not order:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        detalle_pedido = [
        {
            "idPedido": row[0],
            "nombre": row[1],
            "cantidad": row[2],
            "valor unitario": row[3] / row[2],
            "valor total": row[3]
        }
        for row in result
        ]
        return {"detalle_pedido": detalle_pedido,"datos_pedido":order}
    except Exception as e:
        raise e
    

@pedidosR.post("/create_order",summary="Este endpoint crea un pedido",status_code=status.HTTP_201_CREATED,tags=["Pedido"])
def create_order(pedido: PedidoAggPydantic, productos: List[ProductosPedAggPydantic] = None,
                 db: Session = Depends(get_db)):
    # Obtener la fecha actual
    fecha_actual = datetime.now()
    fecha_pedido = fecha_actual.strftime("%Y-%m-%d")
    fecha_entrega_str = pedido.fechaEntrega.strftime("%Y-%m-%d")
    vendedor = decode_token(pedido.token)
    db_pedido = Pedido_table(
                              documentoCliente = pedido.documentoCliente,
                              idVendedor = vendedor["id"],
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
        #db.commit()
    # Actualiza el valor total del pedido
    db_pedido.valorTotal = valorTotalPed
    # Realiza el commit de los cambios en la sesión
    db.commit()

    return Response(status_code=status.HTTP_201_CREATED, content="Pedido creado exitosamente")

@pedidosR.put(
    "/edit_product_state_delivered/{id}",
    status_code= status.HTTP_200_OK ,
    tags=["Pedido"]
)
def update_state_delivered(
    id:int,db: Session = Depends(get_db)
):
    if not isinstance(id, int) or id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El ID del pedido debe ser un número entero positivo"
        )
    # Verificar si el pedido existe en la base de datos
    existing_order = conn.execute(
        select(Pedido_table).where(Pedido_table.idPedido == id)
    ).fetchone()
    if not existing_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El pedido no existe"
        )

    try:
        # Crear la consulta para actualizar el pedido en la base de datos
        query = (
            update(Pedido_table)
            .where(Pedido_table.idPedido == id)
            .values(
                estado = "Entregado"
            )
        )
        # Ejecutar la consulta para actualizar el producto en la base de datos
        db.execute(query)

        # Realizar el commit para guardar los cambios en la base de datos
        db.commit()

        return {"mensaje" : "El pedido se marcó como entregado exitosamente"}
    except Exception as e:
        # Manejar errores en la base de datos u otros errores inesperados
        error_message = "Error interno del servidor"
        if isinstance(e, SQLAlchemyError):
            error_message = str(e.__dict__['orig'])

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        )
    
@pedidosR.put(
    "/edit_product_state_canceled/{id}",
    status_code= status.HTTP_200_OK ,
    tags=["Pedido"]
)
def update_state_canceled(
    id:int,db: Session = Depends(get_db)
):
    if not isinstance(id, int) or id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El ID del pedido debe ser un número entero positivo"
        )
    # Verificar si el pedido existe en la base de datos
    existing_order = conn.execute(
        select(Pedido_table).where(Pedido_table.idPedido == id)
    ).fetchone()
    if not existing_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El pedido no existe"
        )

    try:
        # Crear la consulta para actualizar el pedido en la base de datos
        query = (
            update(Pedido_table)
            .where(Pedido_table.idPedido == id)
            .values(
                estado = "Cancelado"
            )
        )
        # Ejecutar la consulta para actualizar el producto en la base de datos
        db.execute(query)

        productos = conn.execute(
                select(DetallePedido_table).where(DetallePedido_table.idPedido == id)
            ).fetchall()
        for producto in productos:
            producto_to_update = conn.execute(select(Producto_table).where(Producto_table.idProducto == producto.idProducto)).fetchone()
            new_cantity = producto_to_update.cantidad + producto.cantidad
            conn.execute(update(Producto_table).where(Producto_table.idProducto == producto_to_update.idProducto).values(cantidad=new_cantity))

        # Realizar el commit para guardar los cambios en la base de datos
        db.commit()

        return {"mensaje" : "El pedido se marcó como cancelado exitosamente"}
    except Exception as e:
        # Manejar errores en la base de datos u otros errores inesperados
        error_message = "Error interno del servidor"
        if isinstance(e, SQLAlchemyError):
            error_message = str(e.__dict__['orig'])

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        )