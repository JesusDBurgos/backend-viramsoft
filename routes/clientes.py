from fastapi import APIRouter, Depends, Response, status
from config.database import conn,get_db
from models.index import Cliente_table
from schemas.index import ClientePydantic
from sqlalchemy.orm import Session
from sqlalchemy import select,update

clientesR = APIRouter()

@clientesR.get("/costumer", status_code=status.HTTP_200_OK,summary="Este endpoint consulta todos los clientes", tags=["Clientes"])
def get_costumers(db: Session = Depends(get_db)):
    """
    Obtiene todos los clientes desde la base de datos.

    Args:
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con la lista de clientes.
    """
    # Consultar todos los clientes de la base de datos utilizando SQLAlchemy
    clientes = db.query(Cliente_table).all()
    # Devolver una respuesta JSON con la lista de clientes obtenidos
    return {"clientes": clientes}

# Endpoint para buscar un cliente por su ID

@clientesR.get("/costumer/{id}",response_model=ClientePydantic,summary="Este endpoint consulta un producto por su id", status_code=status.HTTP_200_OK,tags=["Clientes"])
def search_costumer(id:str,db: Session = Depends(get_db)):
    """
    Busca un cliente por su ID.

    Args:
        id (str): ID del cliente a buscar.
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con los datos del cliente encontrado.
    """
    # Construir la consulta SELECT utilizando SQLAlchemy
    query = select(Cliente_table).where(Cliente_table.documento == id)
    # Ejecutar la consulta en la base de datos
    resultado = conn.execute(query)
    # Obtener el primer resultado de la consulta
    cliente = resultado.fetchone()
    # Si no se encuentra el producto, devolver una respuesta 404
    if not cliente:
        return Response(status_code=status.HTTP_404_NOT_FOUND, content="cliente no encontrado")
    # Convertir la tupla en un diccionario y convertir el ID a una cadena
    cliente_dict = cliente._asdict()
    # Devolver el producto encontrado en formato JSON utilizando el modelo ClientePydantic
    return ClientePydantic(**cliente_dict)

# Endpoint para crear un nuevo producto

@clientesR.post("/create_costumer",summary="Este endpoint crea un cliente",response_model=ClientePydantic,status_code=status.HTTP_201_CREATED,tags=["Clientes"])
def create_product(cliente: ClientePydantic, db: Session = Depends(get_db)):
    """
    Crea un nuevo cliente en la base de datos.

    Args:
        cliente (ClientePydantic): Datos del cliente a crear.
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con los datos del nuevo cliente creado.
    """
    # Crear un nuevo objeto Cliente_table utilizando los datos proporcionados en el cuerpo de la solicitud
    db_product = Cliente_table(documento = cliente.documento,
                                nombre = cliente.nombre,
                                apellido= cliente.apellido,
                                direccion= cliente.direccion,
                                telefono= cliente.telefono)
    # Agregar el nuevo producto a la sesión de la base de datos
    db.add(db_product)
    # Confirmar los cambios en la base de datos
    db.commit()
    # Refrescar el objeto para asegurarse de que los cambios se reflejen en el objeto en memoria
    db.refresh(db_product)
    # Devolver el nuevo producto creado en formato JSON
    return db_product

# Endpoint para modificar un cliente

@clientesR.put("/edit_costumer/{id}",response_model=ClientePydantic, status_code=status.HTTP_200_OK, tags=["Clientes"])
async def update_data(id: str, cliente: ClientePydantic):
    """
    Modifica un cliente de la base de datos.

    Parámetros:
    - cliente: Los datos del cliente a editar.

    Respuestas:
    - 200 OK: Si el cliente se crea correctamente.
        - Devuelve el nuevo cliente modificado en formato ClientePydantic (JSON).
    """
    # Crear la consulta para actualizar el cliente en la base de datos
    query = update(Cliente_table).where(Cliente_table.documento == id).values(
                    documento = cliente.documento,
                    nombre = cliente.nombre,
                    apellido= cliente.apellido,
                    direccion= cliente.direccion,
                    telefono= cliente.telefono)
    # Ejecutar la consulta para actualizar el cliente en la base de datos
    cliente = conn.execute(query)
    # Crear una consulta para obtener el cliente actualizado
    response = select(Cliente_table).where(Cliente_table.documento == id)
    # Ejecutar la consulta para obtener el cliente actualizado de la base de datos
    response = conn.execute(response).fetchone()
    # Convertir el resultado en un diccionario para modificar el formato
    response = response._asdict()
    # Devolver el cliente actualizado en el formato esperado (ClientePydantic)
    return ClientePydantic(**response)