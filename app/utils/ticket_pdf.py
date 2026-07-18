from io import BytesIO

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def _draw_label_value(pdf, y, label, value):
    pdf.drawString(20 * mm, y, label + ":")
    pdf.drawString(75 * mm, y, str(value))
    return y - 6 * mm


def build_ticket_pdf(bundle: dict) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    transaccion = bundle["transaccion"]
    funcion = bundle.get("funcion")
    tickets = bundle.get("tickets") or []
    seats = bundle.get("seats") or []
    snacks = bundle.get("snacks") or []

    pelicula = funcion.pelicula if funcion else None
    sala = funcion.sala if funcion else None

    pdf.setFillColorRGB(0.11, 0.14, 0.40)
    pdf.rect(0, height - 28 * mm, width, 28 * mm, fill=1, stroke=0)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(20 * mm, height - 18 * mm, "FILMATE - Ticket de Compra")

    pdf.setFillColorRGB(0, 0, 0)
    y = height - 40 * mm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20 * mm, y, "Informacion de la Transaccion")
    y -= 8 * mm

    tipo_compra = "Reserva y dulceria" if tickets and snacks else "Entradas" if tickets else "Solo dulceria"
    pdf.setFont("Helvetica", 10)
    info = [
        ("Transaccion Nro", transaccion.id_transaccion),
        ("Tipo de compra", tipo_compra),
        ("Estado", transaccion.estado_pago),
        ("Metodo de pago", transaccion.metodo_pago or "N/A"),
        ("Pelicula", pelicula.titulo if pelicula else "N/A"),
        ("Sala", sala.nombre_sala if sala else "N/A"),
        ("Fecha funcion", str(funcion.fecha_hora) if funcion else "N/A"),
    ]
    for label, val in info:
        y = _draw_label_value(pdf, y, label, val)

    y -= 4 * mm

    if tickets:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(20 * mm, y, "Entradas")
        y -= 8 * mm

        pdf.setFont("Helvetica", 10)
        for i, ticket in enumerate(tickets):
            seat = seats[i] if i < len(seats) else None
            asiento_str = f"{seat.fila}{seat.columna}" if seat else "N/A"
            pdf.drawString(20 * mm, y, f"Boleto #{ticket.id_ticket} - Asiento {asiento_str}")
            y -= 6 * mm
        y -= 4 * mm

    if snacks:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(20 * mm, y, "Dulceria")
        y -= 8 * mm

        pdf.setFont("Helvetica", 10)
        for item in snacks:
            if y < 45 * mm:
                pdf.showPage()
                y = height - 25 * mm
                pdf.setFont("Helvetica", 10)

            cantidad = item.get("cantidad", 0)
            nombre = item.get("nombre", "Producto")
            precio_unitario = float(item.get("precio_unitario", 0))
            subtotal = float(item.get("subtotal", precio_unitario * cantidad))
            pdf.drawString(20 * mm, y, f"{cantidad} x {nombre}")
            pdf.drawRightString(180 * mm, y, f"S/ {subtotal:.2f}")
            y -= 6 * mm
        y -= 4 * mm

    pdf.line(20 * mm, y, 190 * mm, y)
    y -= 6 * mm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20 * mm, y, "TOTAL PAGADO:")
    pdf.drawString(130 * mm, y, f"S/ {float(transaccion.monto_total):.2f}")
    y -= 12 * mm

    qr_token = f"FILMATE-TXN-{transaccion.id_transaccion}"
    qr_image = qrcode.make(qr_token)
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    pdf.drawImage(ImageReader(qr_buffer), 20 * mm, y - 50 * mm, width=50 * mm, height=50 * mm)

    pdf.setFont("Helvetica", 9)
    pdf.drawString(75 * mm, y - 10 * mm, "Codigo QR de verificacion")
    pdf.drawString(75 * mm, y - 16 * mm, "Transaccion: " + str(transaccion.id_transaccion))
    if not tickets:
        pdf.drawString(75 * mm, y - 22 * mm, "Presenta este QR en dulceria para recoger tu pedido.")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
