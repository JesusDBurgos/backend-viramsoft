from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.index import Base
from databases import Database

DATABASE_URL = "mysql+pymysql://pruebas@34.31.54.110/viramsoft"
engine = create_engine(DATABASE_URL)

conn = engine.connect()

database = Database(DATABASE_URL)

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