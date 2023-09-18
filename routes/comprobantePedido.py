from fastapi import APIRouter, Depends, HTTPException, Query
from io import BytesIO
from config.database import conn,get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.index import DetallePedido_table,Producto_table, Pedido_table, Cliente_table
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from starlette.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

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
    c = canvas.Canvas(response_pdf, pagesize=letter)

    # Agregar el encabezado con el logotipo y la información de la empresa
    c.drawString(100, 750, "Comprobante de Pedido")
    c.drawString(100, 730, f"Fecha de pedido: {fecha_pedido}")
    c.drawString(100, 710, f"Fecha de entrega: {fecha_entrega}")
    c.drawString(100, 690, f"Número de Pedido: {pedido_id}")
    c.drawString(100, 670, f"Cliente: {nombre_cliente}")
    c.drawString(100, 650, f"Dirección: {direccion_cliente}")

    # Crear una tabla para listar los productos
    data = [["Producto", "Cantidad", "Precio Unitario", "Total"]]
    
    total_pedido = 0  # Inicializar el total del pedido en cero

    # Recorrer los detalles del pedido y agregarlos a la tabla
    for detalle_pedido in detalles:
        producto = db.query(Producto_table).filter(Producto_table.idProducto == detalle_pedido.idProducto).first()
        if producto is not None:
            total_producto = detalle_pedido.cantidad * producto.valorVenta
            data.append([producto.nombre, str(detalle_pedido.cantidad), f"${producto.valorVenta:.2f}", f"${total_producto:.2f}"])
            total_pedido += total_producto

    table = Table(data)

    # Establecer el estilo de la tabla
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)

    # Dibujar la tabla en el PDF
    table.wrapOn(c, 400, 600)
    table.drawOn(c, 100, 500)


    # Agregar el total al pie de la página
    c.drawString(100, 100, f"Total del Pedido: ${valor_total:.2f}")

    # Guardar el PDF
    c.save()

    # Mover el puntero al principio del archivo BytesIO
    response_pdf.seek(0)

    # Crear una respuesta de transmisión con el búfer PDF y el tipo de medios "application/pdf"
    response = StreamingResponse(BytesIO(response_pdf.read()), media_type="application/pdf")
    
    # Establecer el encabezado Content-Disposition para controlar el nombre del archivo PDF que se descargará
    response.headers["Content-Disposition"] = f"attachment; filename=comprobante_pedido_{pedido_id}.pdf"

    return response
