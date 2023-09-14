from fastapi import APIRouter, Depends, Response, status, HTTPException, UploadFile, File
from config.database import conn,get_db
from models.index import Producto_table, ImagenProducto
from schemas.index import ProductoPydantic,ProductoUpdatePydantic, ProductosCatPydantic, ProductosIdPydantic
from sqlalchemy.orm import Session
from sqlalchemy import select,update
from typing import List
import locale
import asyncio

productosR = APIRouter()

# Endpoint para obtener todos los productos

async def async_get_products(db: Session):
    """
    Obtiene todos los productos desde la base de datos.

    Args:
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con la lista de productos.
    """
    # Realiza una consulta asincrónica utilizando la sesión existente
    products = await asyncio.to_thread(db.query(Producto_table).all)
    # Procesa los resultados aquí, si es necesario
    return {"productos": products}

@productosR.get("/product", status_code=status.HTTP_200_OK, summary="Este endpoint consulta todos los productos", tags=["Productos"])
async def get_products(db: Session = Depends(get_db)):
    # Utiliza asyncio para ejecutar la función asincrónica y obtener los resultados
    result = await async_get_products(db)
    return result

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

@productosR.post("/cargar_imagen", summary="Cargar una imagen y guardarla en la base de datos", tags=["Imagen"])
def cargar_imagen(imagen: UploadFile = File(...),producto_id = int,db: Session = Depends(get_db)):
    """
    Carga una imagen y la guarda en la base de datos.

    Args:
        producto_id (int): ID del producto al que se asocia la imagen.
        imagen (UploadFile): Imagen a cargar y guardar en la base de datos.
    Returns:
        dict: Un diccionario JSON con un mensaje de éxito.
    """
    # Consultar si ya existe una imagen para el producto
    existing_image = db.query(ImagenProducto).filter(ImagenProducto.producto_id == producto_id).first()

    # Leer los datos binarios de la imagen
    imagen_data = imagen.file.read()

    if existing_image:
        # Si existe una imagen, actualiza sus datos
        existing_image.imagen = imagen_data
    else:
        # Si no existe una imagen, crea una nueva fila en la base de datos
        db_image = ImagenProducto(imagen=imagen_data, producto_id=producto_id)
        db.add(db_image)

    db.commit()

    return {"mensaje": "Imagen cargada y guardada correctamente en la base de datos"}


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
        
        # Devolver el producto actualizado en el formato esperado (ProductoPydantic)
        return updated_product
    except Exception as e:
        # Manejar errores en la base de datos u otros errores inesperados
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")


# @productosR.delete("/")
# async def delete_data():
#     conn.execute(Producto_table.delete().where(Producto_table.c.idProducto == id))
#     return conn.execute(Producto_table.select()).fetchall()