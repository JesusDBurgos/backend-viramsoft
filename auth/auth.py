from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.index import User
from auth.jwt import create_access_token, decode_token, hash_password, verify_password
from schemas.auth import UserLogin,UserRegister
from models.auth import User
from config.database import get_db

auth_router = APIRouter()

@auth_router.post("/login", summary="Este endpoint hace el login en la aplicacion movil", status_code=status.HTTP_202_ACCEPTED)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    # Buscar al usuario en la base de datos por su nombre de usuario
    user = db.query(User).filter(User.username == user_login.username, User.rol == "Vendedor").first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    # Verificar la contraseña del usuario
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    # Generar el token JWT para el usuario autenticado
    access_token = create_access_token({"id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/login_web", summary="Este endpoint hace el login en la aplicacion web", status_code=status.HTTP_202_ACCEPTED)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    # Buscar al usuario en la base de datos por su nombre de usuario
    user = db.query(User).filter(User.username == user_login.username,User.rol == "Administrador").first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    # Verificar la contraseña del usuario
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    # Generar el token JWT para el usuario autenticado
    access_token = create_access_token({"sub": user.username, "name": user.nombre})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/user_register",summary="Este endpoint hace el registro del usuario en la base de datos y encripta la contraseña")
def register(user_register: UserRegister, db: Session = Depends(get_db)):
    # Verificar si el nombre de usuario ya está en uso
    user = db.query(User).filter(User.username == user_register.username).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nombre de usuario ya registrado")
    
    # Crear un nuevo usuario y guardar en la base de datos
    new_user = User(username=user_register.username, hashed_password=hash_password(user_register.password),nombre=user_register.nombre,rol=user_register.rol)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario registrado exitosamente"}

@auth_router.get("/users",summary="Este endpoint consulta los usuarios", status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    """
    Obtiene todos los usuarios desde la base de datos.

    Args:
        db (Session): Objeto de sesión de la base de datos.

    Returns:
        dict: Un diccionario JSON con la lista de usuarios.
    """
    # Consultar todos los productos de la base de datos utilizando SQLAlchemy
    users = db.query(User.id, User.username, User.nombre, User.rol).all()
    
    # Verificar si hay productos. Si no hay productos, lanzar una excepción 404 (Not Found)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron usuarios")
    
    # Crear una lista para almacenar los pedidos formateados
    formatted_users = []
    # Recorrer la lista de pedidos y construir el diccionario de respuesta
    for user in users:
        user_dict = {
            "id": user.id,
            "username": user.username,
            "nombre": user.nombre,
            "rol": user.rol,
        }
        formatted_users.append(user_dict)

    # Devolver una respuesta JSON con la lista de pedidos formateados
    return {"usuarios": formatted_users}