from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.jwt import create_access_token, decode_token, hash_password, verify_password
from schemas.auth import UserLogin
from models.auth import User
from config.database import get_db

auth_router = APIRouter()

@auth_router.post("/login")
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    # Buscar al usuario en la base de datos por su nombre de usuario
    user = db.query(User).filter(User.username == user_login.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    # Verificar la contraseña del usuario
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    # Generar el token JWT para el usuario autenticado
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/user_register")
def register(user_login: UserLogin, db: Session = Depends(get_db)):
    # Verificar si el nombre de usuario ya está en uso
    user = db.query(User).filter(User.username == user_login.username).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nombre de usuario ya registrado")
    
    # Crear un nuevo usuario y guardar en la base de datos
    new_user = User(username=user_login.username, hashed_password=hash_password(user_login.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Usuario registrado exitosamente"}