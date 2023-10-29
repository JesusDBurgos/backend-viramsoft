from sqlalchemy import Column, Integer, String
from models.base import Base

class User(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    nombre = Column( String(255), nullable=False)
    rol = Column( String(50), nullable=False)
    hashed_password = Column(String(255))