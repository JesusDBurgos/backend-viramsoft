from fastapi import APIRouter, Depends, HTTPException, Query
from io import BytesIO
from config.database import conn, get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.index import (
    DetallePedido_table,
    Producto_table,
    Pedido_table,
    Cliente_table,
)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from starlette.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.platypus.flowables import KeepTogether
import base64

comprobantePedido = APIRouter()


@comprobantePedido.get("/generar_comprobante")
async def generar_comprobanteP(
    pedido_id: int = Query(
        ..., description="ID del producto a incluir en el comprobante"
    ),
    db: Session = Depends(get_db),
):
    detalles = db.query(DetallePedido_table).filter(
        DetallePedido_table.idPedido == pedido_id
    )

    pedido = db.query(Pedido_table).filter(Pedido_table.idPedido == pedido_id).first()

    if pedido:
        # Acceder al atributo documentoCliente del objeto Pedido
        documento_cliente = pedido.documentoCliente
        vendedor = pedido.vendedor
        valor_total = pedido.valorTotal
        fecha_pedido = pedido.fechaPedido
        fecha_entrega = pedido.fechaEntrega
    # Realizar otras operaciones con documento_cliente si es necesario
    else:
        # Manejar el caso en el que no se encontró el pedido
        raise HTTPException(status_code=404, detail="Pedido no existe")

    if detalles is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    cliente = (
        db.query(Cliente_table)
        .filter(Cliente_table.documento == documento_cliente)
        .first()
    )

    if cliente:
        nombre_cliente = cliente.nombre
        direccion_cliente = cliente.direccion
        telefono_cliente = cliente.telefono
    else:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # Crear un objeto de lienzo PDF
    response_pdf = BytesIO()
    # Crear un archivo PDF en blanco
    doc = SimpleDocTemplate(response_pdf, pagesize=letter)

    # Lista de elementos para el PDF
    elements = []

    # Obtener los estilos de muestra
    styles = getSampleStyleSheet()
    # Defino el estilo del titulo
    style_title = styles["Normal"]
    style_title.alignment = 1  # 0: Izquierda, 1: Centro, 2: Derecha
    style_title.fontName = "Helvetica-Bold"
    style_title.spaceAfter = 20
    style_title.fontSize = 16
    # Defino el estilo de los items del encabezado
    style_left = styles["Normal"].clone("style_left")
    style_left.alignment = 0
    style_left.fontName = "Helvetica"
    style_left.fontSize = 11
    style_left.spaceAfter = 15
    style_left_encabezado = styles["Normal"].clone("style_left_encabezado")
    style_left_encabezado.alignment = 0
    style_left_encabezado.fontName = "Helvetica-Bold"
    style_left_encabezado.fontSize = 14
    style_left_encabezado.spaceBefore = 15
    # Defino estilo del valor total del pedido
    style_bold_total = styles["Normal"].clone("style_bold_total")
    style_bold_total.alignment = 2
    style_bold_total.fontName = "Helvetica-Bold"
    style_bold_total.fontSize = 14
    style_bold_total.spaceBefore = 25

    fecha_juntas = Paragraph(
        f"<b>Número de Pedido:</b> {pedido_id} &nbsp;&nbsp;&nbsp; <b>Fecha de pedido:</b> {fecha_pedido} &nbsp;&nbsp;&nbsp;&nbsp; <b>Fecha de entrega:</b> {fecha_entrega}",
        style_left,
    )
    cliente = Paragraph(
        f"<b>Cliente:</b> {nombre_cliente} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Dirección:</b> {direccion_cliente} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Teléfono:</b> {telefono_cliente}",
        style_left,
    )
    vendedor_texto = Paragraph(
        f"<b>Vendedor:</b> {vendedor}",
        style_left,
    )

    # Encabezado
    elements.append(Paragraph("Viramsoft", style_title))
    elements.append(Paragraph(f"Comprobante de Pedido", style_left_encabezado))
    elements.append(fecha_juntas)
    elements.append(cliente)
    elements.append(vendedor_texto)

    # Crear una tabla para listar los productos
    data = [["Producto", "Cantidad", "Precio Unitario", "Total"]]

    # Recorrer los detalles del pedido y agregarlos a la tabla
    for detalle_pedido in detalles:
        producto = (
            db.query(Producto_table)
            .filter(Producto_table.idProducto == detalle_pedido.idProducto)
            .first()
        )
        if producto is not None:
            data.append(
                [
                    producto.nombre,
                    str(detalle_pedido.cantidad),
                    f"${detalle_pedido.precio/detalle_pedido.cantidad:.2f}",
                    f"${detalle_pedido.precio:.2f}",
                ]
            )

    # Crear la tabla y aplicar estilos

    table = Table(data, colWidths=[200, 70, 100, 100])

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    # Agregar la tabla al PDF
    elements.append(table)

    # Agregar el total al pie de la página
    elements.append(
        Paragraph(f"Total del Pedido: ${valor_total:.2f}", style_bold_total)
    )

    # Construir el PDF
    doc.build(elements)

    # Mover el puntero al principio del archivo BytesIO
    response_pdf.seek(0)

    # Leer los datos del PDF como bytes
    pdf_bytes = response_pdf.read()

    # Codificar los bytes del PDF en base64
    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

    # Crear una respuesta JSON que contenga el PDF en base64
    return {pdf_base64}