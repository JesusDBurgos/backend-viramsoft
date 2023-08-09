from fastapi import APIRouter, Depends, Response, status, HTTPException
from config.database import conn,get_db
from models.index import Producto_table
from schemas.index import ProductoPydantic,ProductoUpdatePydantic, ProductosCatPydantic
from sqlalchemy.orm import Session
from sqlalchemy import select,update
from typing import List
import locale

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
    # Verificar si hay productos. Si no hay productos, lanzar una excepción 404 (Not Found)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron productos")
    # Formatear los precios en formato de moneda
    for product in products:
        product.valorVenta = "{:,.0f}".format(product.valorVenta).replace(",", ".")
        product.valorCompra = "{:,.0f}".format(product.valorCompra).replace(",", ".")
    # Devolver una respuesta JSON con la lista de productos obtenidos
    return {"productos": products}

# Endpoint para buscar un producto por su Categoria

@productosR.get("/products/{categoria}",response_model=List[ProductoPydantic],summary="Este endpoint consulta un producto por su categoría", status_code=status.HTTP_200_OK,tags=["Productos"])
def search_product_by_category(categoria:str,db: Session = Depends(get_db)):
    """
    Busca un producto por su Categoría.

    Args:
        categoria (str): categoría de los productos a buscar.
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con los datos del producto encontrado.
    """
    # Construir la consulta SELECT utilizando SQLAlchemy
    query = select(Producto_table).where(Producto_table.categoria == categoria)
    # Ejecutar la consulta en la base de datos
    resultado = conn.execute(query)
    # Obtener el primer resultado de la consulta
    productos = resultado.fetchall()
    # Si no se encuentra el producto, devolver una respuesta 404
    if not productos:
        return []
    # Convertir los resultados en una lista de instancias de ProductoPydantic
    productos_response = [ProductoPydantic(**producto._asdict()) for producto in productos]
    # Formatear los precios en formato de moneda
    for producto in productos_response:
        producto.valorVenta = "{:,.0f}".format(producto.valorVenta).replace(",", ".")
        producto.valorCompra = "{:,.0f}".format(producto.valorCompra).replace(",", ".")
    return productos_response

#Endpoint para buscar un producto por su ID 
@productosR.get("/product/{id}",summary="Este endpoint consulta un producto por su id", status_code=status.HTTP_200_OK,tags=["Productos"])
def search_product_by_id(id:int):
    """
    Busca un producto por su Id.

    Args:
        id (int): id de los productos a buscar.
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con los datos del producto encontrado.
    """
    # Ejecutar la consulta en la base de datos
    producto = conn.execute(select(Producto_table).where(Producto_table.idProducto == id)).fetchone()
    print(producto)
    # Si no se encuentra el producto, devolver una respuesta 404
    if not producto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe")
    # Convertir el resultado en un diccionario para el ID
    response = producto._asdict()
    # Formatear los precios en formato de moneda
    response['valorVenta'] = "{:,.0f}".format(response['valorVenta']).replace(",", ".")
    response['valorCompra'] = "{:,.0f}".format(response['valorCompra']).replace(",", ".")
    # Devolver el producto encontrado en formato JSON utilizando el modelo ProductoPydantic
    return response

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
    db_product = Producto_table(nombre = producto.nombre,marca = producto.marca,categoria= producto.categoria, cantidad = producto.cantidad, 
                          valorCompra= producto.valorCompra, valorVenta= producto.valorVenta,
                          unidadMedida= producto.unidadMedida)
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
def update_data(id: int, producto: ProductoUpdatePydantic,db: Session = Depends(get_db)):
    # Verificar si el producto existe en la base de datos
    existing_product = conn.execute(select(Producto_table).where(Producto_table.idProducto == id)).fetchone()
    if not existing_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe")
    
    # Crear la consulta para actualizar el producto en la base de datos
    query = update(Producto_table).where(Producto_table.idProducto == id).values(
        cantidad = producto.cantidad,
        valorCompra = producto.valorCompra,
        valorVenta = producto.valorVenta)
    try:
        # Ejecutar la consulta para actualizar el producto en la base de datos
        db.execute(query)

        # Realizar el commit para guardar los cambios en la base de datos
        db.commit()

        # Crear una consulta para obtener el producto actualizado
        updated_product = db.query(Producto_table).filter(Producto_table.idProducto == id).first()
        # Formatear los precios en formato de moneda
        updated_product.valorVenta = "{:,.0f}".format(updated_product.valorVenta).replace(",", ".")
        updated_product.valorCompra = "{:,.0f}".format(updated_product.valorCompra).replace(",", ".")

        # Devolver el producto actualizado en el formato esperado (ProductoPydantic)
        return updated_product
    except Exception as e:
        # Manejar errores en la base de datos u otros errores inesperados
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")


# @productosR.delete("/")
# async def delete_data():
#     conn.execute(Producto_table.delete().where(Producto_table.c.idProducto == id))
#     return conn.execute(Producto_table.select()).fetchall()