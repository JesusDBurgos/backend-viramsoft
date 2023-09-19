from fastapi import APIRouter, Depends,status, Response, HTTPException
from config.database import conn,get_db
from models.index import Pedido_table,DetallePedido_table, Producto_table, Cliente_table
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

        # datos_pedido = [
        # {
        #     "idPedido": rows[0],
        #     "documentoCliente": rows[1],
        #     "observacion": rows[2] ,
        #     "fechaPedido": rows[3],
        #     "fechaEntrega":rows[4] ,
        #     "valorTotal": rows[5],
        #     "estado": rows[6]
        # }
        # for rows in order
        #]
        # Procesar los resultados aquí
        detalle_pedido = [
        {
            "idPedido": row[0],
            "nombre": row[1],
            "cantidad": row[2],
            "valor unitario": row[3],
            "valor total": row[4]
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