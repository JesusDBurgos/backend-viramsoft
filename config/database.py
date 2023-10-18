from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.index import Base

engine = create_engine("mysql+pymysql://root:viramsoftsena@34.176.76.49/viramsoft")

conn = engine.connect()

SessionLocal = sessionmaker(engine)

# Crear las tablas en la base de datos

def create_tables():
    Base.metadata.create_all(engine)

# Obtener la sesión de la base de datos

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()