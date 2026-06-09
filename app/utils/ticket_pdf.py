from io import BytesIO

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def build_ticket_pdf(bundle: dict) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    transaccion = bundle["transaccion"]
    funcion = bundle["funcion"]
    tickets = bundle["tickets"]
    seats = bundle["seats"]
    qr_payload = bundle["qr_payload"]

    pelicula = funcion.pelicula
    sala = funcion.sala

    pdf.setFillColorRGB(0.11, 0.14, 0.40)
    pdf.rect(0, height - 28 * mm, width, 28 * mm, fill=1, stroke=0)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(20 * mm, height - 18 * mm, "FILMATE — Ticket de Compra")

    pdf.setFillColorRGB(0, 0, 0)
    y = height - 40 * mm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20 * mm, y, "Información de la Transacción")
    y -= 8 * mm

    pdf.setFont("Helvetica", 10)
    info = [
        ("Transacción N°", str(transaccion.id_transaccion)),
        ("Estado", transaccion.estado_pago),
        ("Método de pago", transaccion.metodo_pago or "N/A"),
        ("Película", pelicula.titulo if pelicula else "N/A"),
        ("Sala", sala.nombre_sala if sala else "N/A"),
        ("Fecha", str(funcion.fecha_hora)),
    ]
    for label, val in info:
        pdf.drawString(20 * mm, y, label + ":")
        pdf.drawString(75 * mm, y, val)
        y -= 6 * mm

    y -= 4 * mm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20 * mm, y, "Entradas")
    y -= 8 * mm

    pdf.setFont("Helvetica", 10)
    for i, ticket in enumerate(tickets):
        seat = next((s for s in seats if s.id_asiento == (ticket.id_asiento if hasattr(ticket, "id_asiento") else i)), None)
        asiento_str = f"{seat.fila}{seat.columna}" if seat else str(ticket.id_asiento if hasattr(ticket, "id_asiento") else i)
        pdf.drawString(20 * mm, y, f"Boleto #{ticket.id_ticket} — Asiento {asiento_str}")
        y -= 6 * mm

    y -= 4 * mm

    pdf.line(20 * mm, y, 190 * mm, y)
    y -= 6 * mm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20 * mm, y, "TOTAL PAGADO:")
    pdf.drawString(130 * mm, y, f"S/ {float(transaccion.monto_total):.2f}")
    y -= 12 * mm

    qr_image = qrcode.make(qr_payload.payload_json)
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    pdf.drawImage(ImageReader(qr_buffer), 20 * mm, y - 50 * mm, width=50 * mm, height=50 * mm)

    pdf.setFont("Helvetica", 9)
    pdf.drawString(75 * mm, y - 10 * mm, "Código QR de verificación")
    pdf.drawString(75 * mm, y - 16 * mm, "Transacción: " + str(transaccion.id_transaccion))

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()
