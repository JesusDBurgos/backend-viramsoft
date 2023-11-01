from collections import defaultdict
from fastapi import APIRouter, Depends,status, Response, HTTPException, Query
from config.database import conn,get_db
from models.index import Pedido_table,DetallePedido_table, Producto_table, Cliente_table
from schemas.index import PedidoAggPydantic,ProductoPydantic, ProductosPedAggPydantic 
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select,update, text,desc, func
from datetime import datetime, timedelta
import calendar
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
            labels.append(fecha_inicial_semana.strftime("%Y/%m/%d"))
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

@dashboardR.get("/indicadores_dashboard")
def obtener_ventas_por_semana(
    db: Session = Depends(get_db)
):
    # Obtener la fecha actual
    fecha_actual = datetime.now()
    fecha_actual = fecha_actual 
    # Obtén el primer día del mes actual
    primer_dia_mes_actual = fecha_actual.replace(day=1).replace(hour=0).replace(minute=0).replace(second=0).replace(microsecond=0)
    ultimo_dia_mes_actual = fecha_actual.replace(day=calendar.monthrange(fecha_actual.year, fecha_actual.month)[1]).replace(hour=23).replace(minute=59).replace(second=59)

    print(primer_dia_mes_actual,ultimo_dia_mes_actual)
    
    total_pedidos = (
        db.query(func.sum(Pedido_table.valorTotal))
        .filter(Pedido_table.fechaEntrega <= ultimo_dia_mes_actual, Pedido_table.fechaEntrega >= primer_dia_mes_actual, Pedido_table.estado == "Entregado")
        .scalar()  # Utiliza scalar() para obtener un único valor en lugar de una tupla
    )

    pedidos_entregados = (
        db.query(func.count(Pedido_table.valorTotal))
        .filter(Pedido_table.fechaEntrega <= ultimo_dia_mes_actual, Pedido_table.fechaEntrega >= primer_dia_mes_actual, Pedido_table.estado == "Entregado")
        .scalar()  # Utiliza scalar() para obtener un único valor en lugar de una tupla
    )

    ultimos_pedidos = (
        db.query(Pedido_table)
        .filter(Pedido_table.fechaEntrega <= ultimo_dia_mes_actual, Pedido_table.fechaEntrega >= primer_dia_mes_actual, Pedido_table.estado == "Entregado")
        .order_by(desc(Pedido_table.fechaEntrega))
        .limit(8)
        .all()
    )

    clientes_nuevos = (db.query(func.count(Cliente_table.documento)).filter(Cliente_table.fecha_agregado <= ultimo_dia_mes_actual, Cliente_table.fecha_agregado >= primer_dia_mes_actual, Cliente_table.estado == "ACTIVO").scalar())

    valores = {}

    valores["total_pedidos"] = f"{total_pedidos}"
    valores["pedidos_entregados"] = f"{pedidos_entregados}"
    valores["clientes_nuevos"] = f"{clientes_nuevos}"

    porcentajes = {}


    if primer_dia_mes_actual.month == 1: 
        primer_dia_mes_pasado = primer_dia_mes_actual.replace(year=primer_dia_mes_actual.year - 1, month=12)
    else:
        primer_dia_mes_pasado = primer_dia_mes_actual.replace(month=primer_dia_mes_actual.month - 1)

    # Calcular el último día del mes pasado
    if ultimo_dia_mes_actual.month == 1:  # Si el mes actual es enero
        ultimo_dia_mes_pasado = ultimo_dia_mes_actual.replace(year=fecha_actual.year - 1, month=12,day=2)
        ultimo_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=calendar.monthrange(ultimo_dia_mes_pasado.year, ultimo_dia_mes_pasado.month)[1])
    else:
        ultimo_dia_mes_pasado = ultimo_dia_mes_actual.replace(month=ultimo_dia_mes_actual.month - 1,day=5)
        ultimo_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=calendar.monthrange(ultimo_dia_mes_pasado.year, ultimo_dia_mes_pasado.month)[1])

    total_pedidos_mes_pasado = (
        db.query(func.sum(Pedido_table.valorTotal))
        .filter(Pedido_table.fechaEntrega <= ultimo_dia_mes_pasado, Pedido_table.fechaEntrega >= primer_dia_mes_pasado, Pedido_table.estado == "Entregado")
        .scalar()  # Utiliza scalar() para obtener un único valor en lugar de una tupla
    )

    pedidos_entregados_mes_pasado = (
        db.query(func.count(Pedido_table.valorTotal))
        .filter(Pedido_table.fechaEntrega <= ultimo_dia_mes_pasado, Pedido_table.fechaEntrega >= primer_dia_mes_pasado, Pedido_table.estado == "Entregado")
        .scalar()  # Utiliza scalar() para obtener un único valor en lugar de una tupla
    )

    clientes_nuevos_mes_pasado = (db.query(func.count(Cliente_table.documento)).filter(Cliente_table.fecha_agregado <= ultimo_dia_mes_pasado, Cliente_table.fecha_agregado >= primer_dia_mes_pasado, Cliente_table.estado == "ACTIVO").scalar())

    if total_pedidos_mes_pasado is None or total_pedidos_mes_pasado == 0 :
        porc_total_pedidos = 100
    elif total_pedidos is None :
        porc_total_pedidos = 0
    else:
        porc_total_pedidos = ((total_pedidos - total_pedidos_mes_pasado) / total_pedidos_mes_pasado) * 100

    if pedidos_entregados_mes_pasado is None or pedidos_entregados_mes_pasado == 0:
        porc_pedidos_entregados = 100
    elif  pedidos_entregados is None:
        porc_pedidos_entregados = 0
    else:
        porc_pedidos_entregados = ((pedidos_entregados - pedidos_entregados_mes_pasado) / pedidos_entregados_mes_pasado) * 100

    if clientes_nuevos_mes_pasado is None or clientes_nuevos_mes_pasado == 0:
        porc_clientes_nuevos = 100
    elif clientes_nuevos is None: 
        porc_clientes_nuevos = 0
    else:
        porc_clientes_nuevos = ((clientes_nuevos - clientes_nuevos_mes_pasado) / clientes_nuevos_mes_pasado) * 100

    porcentajes["porc_total_pedidos"] = f"{porc_total_pedidos}%"
    porcentajes["porc_pedidos_entregados"] = f"{porc_pedidos_entregados}%"
    porcentajes["porc_clientes_nuevos"] = f"{porc_clientes_nuevos}%"
    print(primer_dia_mes_actual,primer_dia_mes_pasado)

    return valores, ultimos_pedidos, porcentajes