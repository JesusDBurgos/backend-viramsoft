from pydantic import BaseModel

class ImagenBase64Schema(BaseModel):
    imagen_base64: str  # La imagen en formato base64