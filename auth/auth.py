from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
    access_token = create_access_token({"sub": user.username, "name": user.nombre})
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
    user = db.query(User).filter(User.username == user_login.username).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nombre de usuario ya registrado")
    
    # Crear un nuevo usuario y guardar en la base de datos
    new_user = User(username=user_register.username, hashed_password=hash_password(user_register.password),nombre=user_register.nombre,rol=user_register.rol)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario registrado exitosamente"}