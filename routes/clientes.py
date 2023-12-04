from fastapi import APIRouter, Depends, Response, status, HTTPException
from config.database import conn,get_db
from models.index import Cliente_table
from schemas.index import ClientePydantic, ClienteEditarPydantic
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import select,update, and_

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
    clientes = db.query(Cliente_table).select_from(Cliente_table)
    # Convertir los resultados en una lista de diccionarios
    clientes_list = [cliente.__dict__ for cliente in clientes]
    # Devolver una respuesta JSON con la lista de clientes obtenidos
    return {"clientes":clientes_list}

@clientesR.get("/costumer_active", status_code=status.HTTP_200_OK,summary="Este endpoint consulta los clientes con estado ACTIVO", tags=["Clientes"])
def get_costumers_active(db: Session = Depends(get_db)):
    """
    Obtiene los clientes con estado ACTIVO desde la base de datos.

    Args:
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con la lista de clientes.
    """
    # Consultar los clientes de la base de datos utilizando SQLAlchemy
    clientes = db.query(Cliente_table).select_from(Cliente_table).where(Cliente_table.estado == "ACTIVO")
    # Convertir los resultados en una lista de diccionarios
    clientes_list = [cliente.__dict__ for cliente in clientes]
    # Devolver una respuesta JSON con la lista de clientes obtenidos
    return {"clientes":clientes_list}

@clientesR.get("/costumer_inactive", status_code=status.HTTP_200_OK,summary="Este endpoint consulta los clientes con estado INACTIVO", tags=["Clientes"])
def get_costumers_inactive(db: Session = Depends(get_db)):
    """
    Obtiene los clientes con estado INACTIVO desde la base de datos.

    Args:
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con la lista de clientes.
    """
    # Consultar los clientes de la base de datos utilizando SQLAlchemy
    clientes = db.query(Cliente_table).select_from(Cliente_table).where(Cliente_table.estado == "INACTIVO")
    # Convertir los resultados en una lista de diccionarios
    clientes_list = [cliente.__dict__ for cliente in clientes]
    # Devolver una respuesta JSON con la lista de clientes obtenidos
    return {"clientes":clientes_list}

# Endpoint para buscar un cliente por su ID

@clientesR.get("/costumer/{id}",response_model=ClientePydantic,summary="Este endpoint consulta un cliente por su id", status_code=status.HTTP_200_OK,tags=["Clientes"])
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
    query = select(Cliente_table).where(and_(Cliente_table.documento == id, Cliente_table.estado == "ACTIVO"))
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

# Endpoint para crear un nuevo cliente

@clientesR.post("/create_costumer",summary="Este endpoint crea un cliente",response_model=ClientePydantic,status_code=status.HTTP_201_CREATED,tags=["Clientes"])
def create_costumer(cliente: ClientePydantic, db: Session = Depends(get_db)):
    """
    Crea un nuevo cliente en la base de datos.

    Args:
        cliente (ClientePydantic): Datos del cliente a crear.
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con los datos del nuevo cliente creado.
    """
    # Buscar un cliente inactivo con el mismo número de documento
    cliente_existente = db.query(Cliente_table).filter(Cliente_table.documento == cliente.documento).first()
    if cliente_existente:
        if cliente_existente.estado == "INACTIVO":
            # Si se encuentra un cliente inactivo con el mismo número de documento,
            # actualizar su estado a "ACTIVO" y los demás campos con la información proporcionada
            cliente_existente.nombre = cliente.nombre
            cliente_existente.direccion = cliente.direccion
            cliente_existente.telefono = cliente.telefono
            cliente_existente.estado = "ACTIVO"
            # Confirmar los cambios en la base de datos
            db.commit()
            # Refrescar el objeto para asegurarse de que los cambios se reflejen en el objeto en memoria
            db.refresh(cliente_existente)
            # Devolver el cliente actualizado en formato JSON
            return cliente_existente
        # Si el cliente ya existe y está activo, se devuelve un error indicando que ya está registrado
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El cliente ya está registrado y activo.")
    else: 
        fecha_actual = datetime.now()
        # Crear un nuevo objeto Cliente_table utilizando los datos proporcionados en el cuerpo de la solicitud
        db_product = Cliente_table(documento = cliente.documento,
                                    nombre = cliente.nombre,
                                    direccion= cliente.direccion,
                                    telefono= cliente.telefono,
                                    fecha_agregado= fecha_actual,
                                    estado = "ACTIVO")
        # Agregar el nuevo producto a la sesión de la base de datos
        db.add(db_product)
        # Confirmar los cambios en la base de datos
        db.commit()
        # Refrescar el objeto para asegurarse de que los cambios se reflejen en el objeto en memoria
        db.refresh(db_product)
        # Devolver el nuevo producto creado en formato JSON
        return db_product

# Endpoint para modificar un cliente

@clientesR.put("/edit_costumer/{id}",summary="Este endpoint edita el cliente seleccionado por su id",response_model=ClienteEditarPydantic, status_code=status.HTTP_200_OK, tags=["Clientes"])
def update_data(id: str, cliente: ClienteEditarPydantic):
    """
    Modifica un cliente de la base de datos.

    Parámetros:
    - cliente: Los datos del cliente a editar.

    Respuestas:
    - 200 OK: Si el cliente se crea correctamente.
        - Devuelve el nuevo cliente modificado en formato ClientePydantic (JSON).
    """
    # Iniciar una transacción
    trans = conn.begin()
    try:
        # Crear la consulta para actualizar el cliente en la base de datos
        query = update(Cliente_table).where(Cliente_table.documento == id).values(
                        nombre = cliente.nombre,
                        direccion= cliente.direccion,
                        telefono= cliente.telefono)
        # Ejecutar la consulta para actualizar el cliente en la base de datos
        conn.execute(query)
        # Realizar el commit para guardar los cambios en la base de datos
        trans.commit()
    except SQLAlchemyError:
        # Si ocurre un error, revertir la transacción
        trans.rollback()
        raise
    finally:
        # Si la transacción todavía está activa, revertirla
        if trans.is_active:
            trans.rollback()
    # Crear una consulta para obtener el cliente actualizado
    response = select(Cliente_table).where(Cliente_table.documento == id)
    # Ejecutar la consulta para obtener el cliente actualizado de la base de datos
    response = conn.execute(response).fetchone()
    # Convertir el resultado en un diccionario para modificar el formato
    response = response._asdict()
    # Devolver el cliente actualizado en el formato esperado (ClientePydantic)
    return ClientePydantic(**response)

@clientesR.put("/costumer_change_state/{id_cliente}", status_code=200, tags=["Clientes"])
def costumer_change_state(doc_cliente: int,summary="Este endpoint cambia el estado del cliente", db: Session = Depends(get_db)):
    # Obtener el cliente por su idCliente
    cliente = db.query(Cliente_table).filter(Cliente_table.documento == doc_cliente).first()

    # Verificar si el cliente existe
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    elif cliente.estado == "INACTIVO":
        cliente.estado = "ACTIVO"
    elif cliente.estado == "ACTIVO":
        cliente.estado = "INACTIVO"    
    estado = cliente.estado
    # Confirmar los cambios en la base de datos
    db.commit()

    # Devolver una respuesta exitosa
    return {"mensaje":f"El estado del cliente ahora es {estado}"}