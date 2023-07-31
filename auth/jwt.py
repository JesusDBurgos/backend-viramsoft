import jwt
import os
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

# Clave secreta para firmar los tokens
SECRET_KEY = os.getenv("SECRET_KEY")

# Instancia de OAuth2PasswordBearer para obtener el token JWT desde el encabezado de autorización
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Algoritmo de codificación utilizado para los tokens
ALGORITHM = "HS256"

# Tiempo de expiración de los tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def create_access_token(payload: dict):
    # Genera el token JWT firmado con la clave secreta
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Función para decodificar el token JWT y verificar su validez
def decode_token(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        # Verifica y decodifica el token JWT utilizando la clave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        # Si el token no es válido, devuelve un error de autenticación
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )