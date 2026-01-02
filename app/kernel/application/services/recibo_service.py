from io import BytesIO
from datetime import datetime
from decimal import Decimal
import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode import qr
from reportlab.lib.utils import ImageReader

# Utils para convertir números a letras (Simplificado para el ejemplo)
# En producción te sugiero usar la librería 'num2words' configurada en español
def numero_a_letras(monto):
    entero = int(monto)
    decimal = int(round((monto - entero) * 100))
    # Aquí deberías implementar o importar una función completa de conversión
    # Por brevedad, retorno un placeholder, pero DEBES usar 'num2words'
    texto_monto = f"{entero} {decimal}/100 BOLIVIANOS" 
    return f"SON: {texto_monto}".upper()

class ReciboService:
    def __init__(self):
        # Configuración de la Empresa (Datos SIAT)
        self.empresa = {
            "nombre": "CENTRO INFANTIL DATILERA",
            "razon_social": "DATILERA S.R.L.", # Ejemplo
            "nit": "123456789", # NIT Real de Datilera
            "direccion": "Av. Ejemplo #123, Zona Norte",
            "telefono": "4-4444444",
            "municipio": "Cochabamba - Bolivia",
            "actividad": "ENSEÑANZA PREESCOLAR Y PRIMARIA"
        }

    def generar_recibo_pdf(self, datos_pago: dict) -> BytesIO:
        """
        Genera un PDF en memoria con formato SIAT.
        datos_pago: { 'numero_recibo', 'fecha', 'cliente_nombre', 'cliente_ci', 'detalle', 'monto_total', 'usuario_cajero' }
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=LETTER)
        width, height = LETTER

        # --- 1. ENCABEZADO IZQUIERDO (Datos Empresa) ---
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2 * cm, height - 2 * cm, self.empresa["nombre"])
        c.setFont("Helvetica", 8)
        c.drawString(2 * cm, height - 2.4 * cm, self.empresa["direccion"])
        c.drawString(2 * cm, height - 2.8 * cm, f"Tel: {self.empresa['telefono']}")
        c.drawString(2 * cm, height - 3.2 * cm, self.empresa["municipio"])
        
        # Aquí podrías dibujar el logo con c.drawImage(...)

        # --- 2. ENCABEZADO DERECHO (Recuadro Fiscal) ---
        # Coordenadas del recuadro
        rect_x = width - 7 * cm
        rect_y = height - 4 * cm
        rect_w = 5 * cm
        rect_h = 2.5 * cm
        
        c.setLineWidth(0.5)
        c.rect(rect_x, rect_y, rect_w, rect_h)
        
        c.setFont("Helvetica-Bold", 9)
        # NIT
        c.drawCentredString(rect_x + rect_w/2, rect_y + 1.8 * cm, f"NIT: {self.empresa['nit']}")
        # Nro Recibo
        c.drawCentredString(rect_x + rect_w/2, rect_y + 1.2 * cm, f"N° RECIBO: {datos_pago['numero_recibo']}")
        # Cod Autorización (Simulado)
        c.drawCentredString(rect_x + rect_w/2, rect_y + 0.6 * cm, "COD. AUT: INTERNO")

        # --- 3. TÍTULO CENTRAL ---
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, height - 5 * cm, "RECIBO DE PAGO")
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(width / 2, height - 5.5 * cm, self.empresa["actividad"])

        # --- 4. DATOS DEL CLIENTE (Cuerpo) ---
        y_pos = height - 7 * cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2 * cm, y_pos, f"Lugar y Fecha:")
        c.setFont("Helvetica", 9)
        fecha_str = datos_pago['fecha'].strftime("%d/%m/%Y")
        c.drawString(5 * cm, y_pos, f"Cochabamba, {fecha_str}")

        y_pos -= 0.6 * cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2 * cm, y_pos, f"Señor(es):")
        c.setFont("Helvetica", 9)
        c.drawString(5 * cm, y_pos, datos_pago['cliente_nombre'])

        y_pos -= 0.6 * cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2 * cm, y_pos, f"NIT/CI:")
        c.setFont("Helvetica", 9)
        c.drawString(5 * cm, y_pos, datos_pago['cliente_ci'])

        # --- 5. TABLA DE DETALLES ---
        # Cabecera de Tabla
        y_pos -= 1.5 * cm
        c.setFillColor(colors.lightgrey)
        c.rect(2 * cm, y_pos - 0.2*cm, width - 4 * cm, 0.6 * cm, fill=1, stroke=0)
        c.setFillColor(colors.black)
        
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(2.5 * cm, y_pos, "CANT")
        c.drawCentredString(8 * cm, y_pos, "DETALLE / CONCEPTO")
        c.drawCentredString(15 * cm, y_pos, "SUBTOTAL (Bs.)")

        # Items (Iterar si hubiera varios, aquí asumimos 1 concepto principal por pago)
        y_pos -= 0.8 * cm
        c.setFont("Helvetica", 9)
        
        # Cantidad
        c.drawCentredString(2.5 * cm, y_pos, "1")
        # Detalle (Ajustar si es muy largo)
        c.drawString(4 * cm, y_pos, datos_pago['detalle'])
        # Subtotal
        monto_fmt = f"{datos_pago['monto_total']:.2f}"
        c.drawRightString(17 * cm, y_pos, monto_fmt)

        # Línea final de tabla
        y_pos -= 0.5 * cm
        c.line(2 * cm, y_pos, width - 2 * cm, y_pos)

        # --- 6. TOTALES Y LITERAL ---
        y_pos -= 1 * cm
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2 * cm, y_pos, numero_a_letras(datos_pago['monto_total']))
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(13 * cm, y_pos, "TOTAL Bs.")
        c.drawRightString(17 * cm, y_pos, monto_fmt)

        # --- 7. PIE DE PÁGINA (QR y Leyenda) ---
        qr_y = y_pos - 4 * cm
        
        # Generar QR
        qr_data = f"{self.empresa['nit']}|{datos_pago['numero_recibo']}|{fecha_str}|{monto_fmt}|{datos_pago['cliente_ci']}"
        qr_code = qr.QrCodeWidget(qr_data)
        qr_code.barWidth = 80
        qr_code.barHeight = 80
        
        d = Drawing(80, 80)
        d.add(qr_code)
        
        # Renderizar QR en PDF
        from reportlab.graphics import renderPDF
        renderPDF.draw(d, c, 14 * cm, qr_y) # Posición derecha

        # Leyenda Ley 453
        c.setFont("Helvetica", 7)
        c.drawCentredString(width / 2, qr_y, "\"ESTE DOCUMENTO ES UN RECIBO INTERNO, NO VÁLIDO PARA CRÉDITO FISCAL\"")
        c.drawCentredString(width / 2, qr_y - 0.4 * cm, "\"La educación es el arma más poderosa para cambiar el mundo.\"")

        # Usuario Cajero
        c.setFont("Helvetica-Oblique", 6)
        c.drawString(2 * cm, 2 * cm, f"Registrado por: {datos_pago['usuario_cajero']}")
        c.drawString(2 * cm, 1.7 * cm, f"Fecha Impresión: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        c.showPage()
        c.save()
        
        buffer.seek(0)
        return buffer