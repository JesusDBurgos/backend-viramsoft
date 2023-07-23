from fastapi import APIRouter, Depends, Response, status
from config.database import conn,get_db
from models.index import Producto_table
from schemas.index import ProductoPydantic
from sqlalchemy.orm import Session
from sqlalchemy import select,update

productosR = APIRouter()

# Endpoint para obtener todos los productos

@productosR.get("/product", status_code=status.HTTP_200_OK,summary="Este endpoint consulta todos los productos", tags=["Productos"])
def get_products(db: Session = Depends(get_db)):
    """
    Obtiene todos los productos desde la base de datos.

    Args:
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con la lista de productos.
    """
    # Consultar todos los productos de la base de datos utilizando SQLAlchemy
    products = db.query(Producto_table).all()
    # Devolver una respuesta JSON con la lista de productos obtenidos
    return {"productos": products}

# Endpoint para buscar un producto por su ID

@productosR.get("/product/{id}",response_model=ProductoPydantic,summary="Este endpoint consulta un producto por su id", status_code=status.HTTP_200_OK,tags=["Productos"])
def search_product(id:str,db: Session = Depends(get_db)):
    """
    Busca un producto por su ID.

    Args:
        id (str): ID del producto a buscar.
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con los datos del producto encontrado.
    """
    # Construir la consulta SELECT utilizando SQLAlchemy
    query = select(Producto_table).where(Producto_table.idProducto == id)
    # Ejecutar la consulta en la base de datos
    resultado = conn.execute(query)
    # Obtener el primer resultado de la consulta
    producto = resultado.fetchone()
    # Si no se encuentra el producto, devolver una respuesta 404
    if not producto:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="Producto no encontrado")
    # Convertir la tupla en un diccionario y convertir el ID a una cadena
    producto_dict = producto._asdict()
    producto_dict['idProducto'] = str(producto_dict['idProducto'])
    # Devolver el producto encontrado en formato JSON utilizando el modelo ProductoPydantic
    return ProductoPydantic(**producto_dict)

# Endpoint para crear un nuevo producto

@productosR.post("/create_product",summary="Este endpoint crea un producto",status_code=status.HTTP_201_CREATED,tags=["Productos"])
def create_product(producto: ProductoPydantic, db: Session = Depends(get_db)):
    """
    Crea un nuevo producto en la base de datos.

    Args:
        producto (ProductoPydantic): Datos del producto a crear.
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con los datos del nuevo producto creado.
    """
    # Crear un nuevo objeto Producto_table utilizando los datos proporcionados en el cuerpo de la solicitud
    db_product = Producto_table(nombre = producto.nombre, cantidad = producto.cantidad, 
                          valorCompra= producto.valorCompra, valorVenta= producto.valorVenta,
                          unidadMedida= producto.unidadMedida, fechaVencimiento= producto.fechaVencimiento)
    # Agregar el nuevo producto a la sesión de la base de datos
    db.add(db_product)
    # Confirmar los cambios en la base de datos
    db.commit()
    # Refrescar el objeto para asegurarse de que los cambios se reflejen en el objeto en memoria
    db.refresh(db_product)
    # Devolver el nuevo producto creado en formato JSON
    return db_product

# Definir el endpoint para actualizar un producto por su ID
@productosR.put("/edit_product/{id}",response_model=ProductoPydantic, status_code=status.HTTP_200_OK, tags=["Productos"])
async def update_data(id: str, producto: ProductoPydantic):
    # Crear la consulta para actualizar el producto en la base de datos
    query = update(Producto_table).where(Producto_table.idProducto == id).values(
        nombre = producto.nombre,
        cantidad = producto.cantidad,
        valorCompra = producto.valorCompra,
        valorVenta = producto.valorVenta,
        unidadMedida = producto.unidadMedida,
        fechaVencimiento = producto.fechaVencimiento)
    # Ejecutar la consulta para actualizar el producto en la base de datos
    producto = conn.execute(query)
    # Crear una consulta para obtener el producto actualizado
    response = select(Producto_table).where(Producto_table.idProducto == id)
    # Ejecutar la consulta para obtener el producto actualizado de la base de datos
    response = conn.execute(response).fetchone()
    # Convertir el resultado en un diccionario para modificar el formato de la fecha y el ID
    response = response._asdict()
    response['idProducto'] = str(response['idProducto'])
    # Devolver el producto actualizado en el formato esperado (ProductoPydantic)
    return ProductoPydantic(**response)

# @productosR.delete("/")
# async def delete_data():
#     conn.execute(Producto_table.delete().where(Producto_table.c.idProducto == id))
#     return conn.execute(Producto_table.select()).fetchall()