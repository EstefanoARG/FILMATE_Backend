from io import BytesIO

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from app.schemas.ticket import TicketIssueResponse


def build_ticket_pdf(bundle: TicketIssueResponse) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    reserva = bundle.reserva
    snacks  = bundle.snacks or []

    # ── Encabezado ──
    pdf.setFillColorRGB(0.11, 0.14, 0.40)
    pdf.rect(0, height - 28*mm, width, 28*mm, fill=1, stroke=0)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(20*mm, height - 18*mm, "FILMATE — Ticket de Compra")

    pdf.setFillColorRGB(0, 0, 0)
    y = height - 40*mm

    # ── Info reserva ──
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20*mm, y, "Información de la Reserva")
    y -= 8*mm

    pdf.setFont("Helvetica", 10)
    info = [
        ("Reserva N°",    str(reserva.get("id_reserva"))),
        ("Estado",        reserva.get("estado_pago", "")),
        ("Método de pago", reserva.get("metodo_pago") or "N/A"),
        ("Transacción",   reserva.get("transaccion_id") or "N/A"),
    ]
    for label, val in info:
        pdf.drawString(20*mm, y, label + ":")
        pdf.drawString(75*mm, y, val)
        y -= 6*mm

    y -= 4*mm

    # ── Boletos ──
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20*mm, y, "Entradas")
    y -= 8*mm

    pdf.setFont("Helvetica", 10)
    for ticket in bundle.boletos:
        precio = float(ticket.precio_pagado)
        pdf.drawString(20*mm, y, f"Boleto #{ticket.id_boleto} — Asiento {ticket.id_asiento}")
        pdf.drawString(130*mm, y, f"S/ {precio:.2f}")
        y -= 6*mm

    y -= 4*mm

    # ── Snacks ──
    if snacks:
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(20*mm, y, "Dulcería")
        y -= 8*mm

        pdf.setFont("Helvetica", 10)
        for s in snacks:
            pdf.drawString(20*mm, y, f"{s['producto']} × {s['cantidad']}")
            pdf.drawString(130*mm, y, f"S/ {s['subtotal']:.2f}")
            y -= 6*mm

        y -= 4*mm

    # ── Totales ──
    pdf.line(20*mm, y, 190*mm, y)
    y -= 6*mm

    descuento   = float(reserva.get("descuento_aplicado", 0))
    monto_total = float(reserva.get("monto_total", 0))

    if descuento > 0:
        pdf.setFont("Helvetica", 10)
        pdf.drawString(20*mm, y, "Descuento aplicado:")
        pdf.drawString(130*mm, y, f"– S/ {descuento:.2f}")
        y -= 6*mm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(20*mm, y, "TOTAL PAGADO:")
    pdf.drawString(130*mm, y, f"S/ {monto_total:.2f}")
    y -= 12*mm

    # ── QR ──
    qr_image = qrcode.make(bundle.qr.payload_json)
    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    pdf.drawImage(ImageReader(qr_buffer), 20*mm, y - 50*mm, width=50*mm, height=50*mm)

    pdf.setFont("Helvetica", 9)
    pdf.drawString(75*mm, y - 10*mm, "Código QR de verificación")
    pdf.drawString(75*mm, y - 16*mm, "Reserva: " + str(reserva.get("id_reserva")))

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()