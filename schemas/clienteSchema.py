from pydantic import BaseModel

class ClientePydantic(BaseModel):
    documento: str = "109841164"
    nombre: str = "Luis"
    apellido: str = "Perez"
    direccion: str = "Carrera 65 #13-2"
    telefono: str = "3157017745"
