from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.index import productosR, clientesR, pedidosR, comprobantePedido
from auth.auth import auth_router
from config.database import create_tables
from models.index import Cliente_table,Producto_table,DetallePedido_table,Pedido_table,User

app = FastAPI()

# Configurar el origen permitido como comodín para permitir cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(productosR)
app.include_router(clientesR)
app.include_router(pedidosR)
app.include_router(comprobantePedido)

# Inicializar el proyecto
def initialize_project():
    create_tables()

initialize_project()



























# @app.post("/viramsoft", status_code=status.HTTP_201_CREATED, response_model=Producto)
# def read_root(producto: Producto):
#     """
#     # ARGS
#         - product: Product
#     # RESPONSE
#         - product: Product 
#     """

#     tabla_frutas.append(producto)
#     return producto.model_dump_json()

# @app.get("/all",status_code=status.HTTP_200_OK)
# def read_root():
#     return json.loads(json.dumps(tabla_frutas)) # sin los json tambien funciono pero en el tuto salia el casteo así

# @app.get("/{id}",status_code=status.HTTP_200_OK)
# def read_root(id: int):
#     for fruta in tabla_frutas:
#         if fruta["id"] == id:
#             return fruta
#     return {}

# @app.delete("/{id}",status_code=status.HTTP_200_OK)
# def read_root(id: int):
#     for fruta in tabla_frutas:
#         if fruta["id"] == id:
#             fruta_sel= fruta
#             tabla_frutas.remove(fruta_sel)
#             return fruta_sel
#     return {}

# @app.post("/create_product",status_code=status.HTTP_201_CREATED, response_model=Producto, summary="Este endpoint crea un producto")
# def crear_producto(producto: Producto):
#     db = Session()
#     new_producto = Producto(**producto.dict())
#     db.add(new_producto)
#     db.commit()
#     return {producto.dict()}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}