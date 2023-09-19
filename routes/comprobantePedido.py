from fastapi import APIRouter, Depends, HTTPException, Query
from io import BytesIO
from config.database import conn,get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.index import DetallePedido_table,Producto_table, Pedido_table, Cliente_table
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from starlette.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate

comprobantePedido = APIRouter()

def consultar_producto_por_id(id_producto,db: Session = get_db):
    query = select(Producto_table).where(Producto_table.idProducto == id_producto)
    return db.execute(query).first()

    
@comprobantePedido.get("/generar_comprobante")
async def generar_comprobanteP(pedido_id: int = Query(..., description="ID del producto a incluir en el comprobante"),db: Session = Depends(get_db)):
    
    detalles = db.query(DetallePedido_table).filter(DetallePedido_table.idPedido == pedido_id )

    pedido = db.query(Pedido_table).filter(Pedido_table.idPedido == pedido_id ).first()
    
    if pedido:
    # Acceder al atributo documentoCliente del objeto Pedido
        documento_cliente = pedido.documentoCliente
        valor_total = pedido.valorTotal
        fecha_pedido= pedido.fechaPedido
        fecha_entrega = pedido.fechaEntrega
    # Realizar otras operaciones con documento_cliente si es necesario
    else:
    # Manejar el caso en el que no se encontró el pedido
        raise HTTPException(status_code=404, detail="Pedido no existe")
    
    if detalles is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    

    cliente = db.query(Cliente_table).filter(Cliente_table.documento == documento_cliente).first()

    if cliente:
        nombre_cliente = cliente.nombre
        direccion_cliente = cliente.direccion
    else:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Crear un objeto de lienzo PDF
    response_pdf = BytesIO()
    # Crear un archivo PDF en blanco
    doc = SimpleDocTemplate(response_pdf, pagesize=letter)

    # Lista de elementos para el PDF
    elements = []

    # Definir estilos
    styles = getSampleStyleSheet()
    style_center = styles["Normal"]
    style_center.alignment = 1  # 0: Izquierda, 1: Centro, 2: Derecha
    style_bold_center = styles["Normal"]
    style_bold_center.alignment = 1
    style_bold_center.fontName = "Helvetica-Bold"


    # Encabezado
    elements.append(Paragraph("Comprobante de Pedido", style_bold_center))
    elements.append(Paragraph(f"Fecha de pedido: {fecha_pedido}", style_center))
    elements.append(Paragraph(f"Fecha de entrega: {fecha_entrega}", style_center))
    elements.append(Paragraph(f"Número de Pedido: {pedido_id}", style_center))
    elements.append(Paragraph(f"Cliente: {nombre_cliente}", style_center))
    elements.append(Paragraph(f"Dirección: {direccion_cliente}", style_center))
    elements.append(Paragraph("", style_center))  # Espacio en blanco

    # Crear una tabla para listar los productos
    data = [["Producto", "Cantidad", "Precio Unitario", "Total"]]
    
    # Recorrer los detalles del pedido y agregarlos a la tabla
    for detalle_pedido in detalles:
        producto = db.query(Producto_table).filter(Producto_table.idProducto == detalle_pedido.idProducto).first()
        if producto is not None:
            total_producto = detalle_pedido.cantidad * producto.valorVenta
            data.append([producto.nombre, str(detalle_pedido.cantidad), f"${producto.valorVenta:.2f}", f"${total_producto:.2f}"])

    # Crear la tabla y aplicar estilos

    table = Table(data,colWidths=[200, 70, 100, 100])

    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    # Agregar la tabla al PDF
    elements.append(table)
    # # Dibujar la tabla en el PDF
    # table.wrapOn(c, 400, 600)
    # table.drawOn(c, 100, 500)


    # Agregar el total al pie de la página
    elements.append(Paragraph(f"Total del Pedido: ${valor_total:.2f}", style_bold_center))      


    # Construir el PDF
    doc.build(elements) 


    # Mover el puntero al principio del archivo BytesIO
    response_pdf.seek(0)

    # Crear una respuesta de transmisión con el búfer PDF y el tipo de medios "application/pdf"
    response = StreamingResponse(BytesIO(response_pdf.read()), media_type="application/pdf")
    
    # Establecer el encabezado Content-Disposition para controlar el nombre del archivo PDF que se descargará
    response.headers["Content-Disposition"] = f"attachment; filename=comprobante_pedido_{pedido_id}.pdf"

    return response
