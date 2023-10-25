from collections import defaultdict
from fastapi import APIRouter, Depends,status, Response, HTTPException, Query
from config.database import conn,get_db
from models.index import Pedido_table,DetallePedido_table, Producto_table, Cliente_table
from schemas.index import PedidoAggPydantic,ProductoPydantic, ProductosPedAggPydantic 
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select,update, text
from datetime import datetime, timedelta
from itertools import count
from typing import List

dashboardR = APIRouter()

@dashboardR.get("/ventas_por_periodo")
def obtener_ventas_por_periodo(
    semanas_atras: int = Query(4, description="Número de semanas atrás desde la fecha actual"),db: Session = Depends(get_db)
):
    # Validar el parámetro semanas_atras
    if not isinstance(semanas_atras, int) or semanas_atras <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El parámetro semanas_atras debe ser un número entero positivo"
        )
    # Calcula la fecha de inicio y fin del período
    fecha_fin = datetime.now()

    # Inicializa las listas para almacenar las etiquetas (período) y los datos (ventas)
    labels = []
    datos_ventas = []

    with db as db:
        for semana in range(1,semanas_atras + 1):
            total_ventas_semana = 0
            fecha_inicial_semana = fecha_fin - timedelta(weeks=semana)
            fecha_final_semana = fecha_inicial_semana + timedelta(weeks=1)
            print(fecha_inicial_semana)
            print(fecha_final_semana)
            # Realiza la consulta a la base de datos para obtener las ventas en la semana actual
            ventas_semana = (
                db.query(Pedido_table)
                .filter(Pedido_table.estado == "Entregado")
                .filter(fecha_inicial_semana.strftime("%Y-%m-%d") < Pedido_table.fechaEntrega)
                .filter(Pedido_table.fechaEntrega <= fecha_final_semana.strftime("%Y-%m-%d"))
                .all()
            )

            # Calcula el total de ventas en la semana y agrega la etiqueta y el dato correspondiente
            for venta in ventas_semana:
                total_ventas_semana += venta.valorTotal
            labels.append(fecha_final_semana.strftime("%Y/%m/%d") + "-" + fecha_inicial_semana.strftime("%Y/%m/%d"))
            datos_ventas.append(total_ventas_semana)

    # Formatea los datos en la estructura deseada
    data = {
        "labels": labels,
        "data": datos_ventas
    }

    return data

@dashboardR.get("/ventas_por_semana")
def obtener_ventas_por_semana(
    db: Session = Depends(get_db)
):
    # Obtener la fecha actual
    fecha_actual = datetime.now()

    # Calcular la fecha de inicio de la semana que pasó
    fecha_inicio_semana = fecha_actual - timedelta(weeks=1)

    # Calcular la fecha de fin de la semana que pasó
    fecha_fin_semana = fecha_actual

    # Diccionario para almacenar las ventas por día de la semana
    ventas_por_dia = defaultdict(float)

    # Diccionario que mapea los números de día de la semana a nombres en español
    nombres_dias_semana = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo"
    }

    with db as db:
        # Realiza la consulta a la base de datos para obtener las ventas en la semana
        ventas_semana = (
            db.query(Pedido_table)
            .filter(Pedido_table.estado == "Entregado")
            .filter(fecha_inicio_semana <= Pedido_table.fechaEntrega)
            .filter(Pedido_table.fechaEntrega <= fecha_fin_semana)
            .all()
        )

        # Itera sobre los pedidos para obtener las ventas por día
        for venta in ventas_semana:
            print(venta.fechaEntrega)
            # Obtener el día de la semana en numero de la fecha de entrega
            dia_semana = venta.fechaEntrega.weekday()
            print(dia_semana)
            # Obtener el nombre del día de la semana en texto
            dia_semana = nombres_dias_semana.get(dia_semana)
            print(dia_semana)
            # Agregar la etiqueta y el dato correspondiente
            ventas_por_dia[dia_semana] += venta.valorTotal
    # Generar etiquetas de los días de la semana desde hoy hasta hace una semana
    labels = []
    fecha_inicio_semana = fecha_inicio_semana + timedelta(days=1)
    print(fecha_inicio_semana)
    print(fecha_actual)
    while fecha_actual >= fecha_inicio_semana:
        dia_semana = nombres_dias_semana.get(fecha_actual.weekday())  # Obtener el nombre del día de la semana
        fecha_actual -= timedelta(days=1)
        labels.append(dia_semana)
        
    # Llenar datos para los días no presentes en las ventas
    datos_ventas = [ventas_por_dia[dia] for dia in labels]
    # Formatea los datos en la estructura deseada
    data = {
        "labels": labels,
        "data": datos_ventas
    }

    return data

