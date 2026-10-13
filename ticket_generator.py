# ticket_generator.py (VERSIÓN CON AJUSTES VISUALES)
from fpdf import FPDF
import qrcode
import os

TICKET_WIDTH = 80 # Ancho del ticket en mm

class PDF(FPDF):
    def header(self):
        pass
    def footer(self):
        pass # Puedes añadir un pie de página si lo deseas aquí

def create_ticket(data, logo_path, payment_details, output_path):
    """
    Crea un PDF con formato de ticket de 80mm, con ajustes visuales fáciles.
    """
    try:
        # --- AJUSTE 1: MÁRGENES ---
        # Márgenes: izquierdo, superior, derecho. El inferior se ajusta automáticamente.
        pdf = PDF(orientation='P', unit='mm', format=(TICKET_WIDTH, 297))
        pdf.set_margins(left=5, top=10, right=5)
        pdf.add_page()
        
        # --- AJUSTE 2: EL LOGO ---
        if logo_path:
            # Cambia 'w' para hacer el logo más grande o pequeño.
            # Cambia 'x' para moverlo a la izquierda o derecha.
            # Para centrarlo: x = (TICKET_WIDTH - w) / 2
            logo_width = 30
            logo_x = (TICKET_WIDTH - logo_width) / 2
            pdf.image(logo_path, x=logo_x, y=8, w=logo_width)
            # Añade más espacio después del logo si es necesario
            pdf.ln(28)

        # --- AJUSTE 3: DATOS DE TU EMPRESA (Textos fijos) ---
        # Puedes cambiar el texto, el tamaño de la fuente, y la alineación ('C', 'L', 'R')
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, 'MI EMPRESA S.A.C.', ln=1, align='C') # Cambia "MI EMPRESA S.A.C."
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 5, 'AV. EJEMPLO 123 - LIMA', ln=1, align='C') # Cambia la dirección
        pdf.cell(0, 4, f"RUC: 2000000000", ln=1, align='C')
        pdf.cell(0, 4, 'Central telefónica: 999 999 999', ln=1, align='C')
        pdf.cell(0, 4, 'Email: correoejemplo@gmail.com', ln=1, align='C')
        pdf.ln(3) # Espacio extra

        pdf.set_line_width(0.2)
        pdf.line(5, pdf.get_y(), TICKET_WIDTH - 5, pdf.get_y())
        pdf.ln(3)

        # --- AJUSTE 4: DATOS DEL COMPROBANTE ---
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(0, 4, data.get('tipo_documento', 'COMPROBANTE').upper(), ln=1, align='C')
        pdf.cell(0, 4, data.get('numero_documento', 'N/A'), ln=1, align='C')
        pdf.set_font('Arial', '', 8)
        pdf.ln(3)
    
        # --- AJUSTE 5: LÍNEA DIVISORIA ---
        # Puedes cambiar el grosor de la línea
        pdf.set_line_width(0.2)
        pdf.line(5, pdf.get_y(), TICKET_WIDTH - 5, pdf.get_y())
        pdf.ln(3)

        # --- SECCIÓN 1: DATOS GENERALES ---
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(30, 5, 'F. Emisión:')
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 5, data.get('fecha_emision', 'N/A'), ln=1)

        pdf.set_font('Arial', 'B', 8)
        pdf.cell(30, 5, 'F. Vencimiento:')
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 5, data.get('fecha_emision'), ln=1)

        pdf.set_font('Arial', 'B', 8)
        pdf.cell(30, 5, 'Cliente:')
        pdf.set_font('Arial', '', 8)
        pdf.multi_cell(0, 5, data.get('cliente_nombre', 'N/A'), ln=1)
        
        pdf.set_font('Arial', 'B', 8)
        pdf.cell(30, 5, 'DNI:')
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 5, data.get('cliente_ruc_dni', 'N/A'), ln=1)
        pdf.ln(5)

         # --- SECCIÓN: TABLA DE ITEMS (NUEVO DISEÑO) ---
        pdf.set_font('Arial', 'B', 7)
        pdf.line(5, pdf.get_y(), TICKET_WIDTH - 5, pdf.get_y())
        
        # DEFINIMOS EL ANCHO DE CADA COLUMNA
        col_cant_w = 8
        col_desc_w = 38
        col_unit_w = 11
        col_total_w = 13
        
        # ENCABEZADOS DE LA TABLA
        pdf.cell(10, 5, 'CANT', align='C')
        pdf.cell(36, 5, 'DESCRIPCIÓN', align='L')
        pdf.cell(12, 5, 'P.UNIT', align='R')
        pdf.cell(12, 5, 'TOTAL', align='R', ln=1)
        pdf.line(5, pdf.get_y(), TICKET_WIDTH - 5, pdf.get_y())
        pdf.ln(1)

        pdf.set_font('Arial', '', 7)
        y_inicial_item = pdf.get_y()
        pdf.multi_cell(10, 4, data.get('cantidad', ''), align='C')
        pdf.set_xy(15, y_inicial_item)
        pdf.multi_cell(36, 4, data.get('descripcion', 'N/A'), align='L')
        altura_item = pdf.get_y() - y_inicial_item
        pdf.set_xy(51, y_inicial_item)
        pdf.multi_cell(12, altura_item, data.get('valor_unitario', '0.00'), align='R')
        pdf.set_xy(63, y_inicial_item)
        pdf.multi_cell(12, altura_item, data.get('total', '0.00'), align='R')
        pdf.set_y(y_inicial_item + altura_item + 2)

        # --- DESGLOSE DE TOTALES ---
        pdf.line(5, pdf.get_y(), TICKET_WIDTH - 5, pdf.get_y())
        pdf.ln(1)

        def print_total_line(label, value):
            pdf.set_font('Arial', '', 8)
            pdf.cell(30) 
            pdf.cell(20, 5, label, align='R')
            pdf.set_font('Arial', 'B', 8)
            pdf.cell(5, 5, "S/", align='R')
            pdf.cell(15, 5, value, ln=1, align='R')

        print_total_line('Op. Gravada:', data.get('op_gravada', '0.00'))
        print_total_line('IGV:', data.get('igv', '0.00'))
        
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(30)
        pdf.cell(20, 6, 'TOTAL:', align='R')
        pdf.cell(5, 6, "S/", align='R')
        pdf.cell(15, 6, data.get('total', '0.00'), ln=1, align='R')
        pdf.ln(5)

        # --- SECCIÓN AÑADIDA: TOTAL EN LETRAS ---
        pdf.set_font('Arial', '', 7)
        # Usamos multi_cell por si el texto es muy largo y necesita saltar de línea
        pdf.multi_cell(0, 4, f"SON: {data.get('total_letras', 'N/A')}", align='L')
        pdf.ln(5)

        # --- SECCIÓN NUEVA: CONDICIONES DE PAGO ---
        pdf.set_font('Arial', 'B', 8)
        pdf.line(5, pdf.get_y(), TICKET_WIDTH - 5, pdf.get_y())
        pdf.cell(0, 5, 'CONDICIONES DE PAGO', ln=1, align='C')
        pdf.line(5, pdf.get_y(), TICKET_WIDTH - 5, pdf.get_y())
        pdf.ln(2)

        # Mostramos los datos de pago que obtuvimos de la interfaz
        condicion = payment_details.get("condicion")
        if condicion:
            pdf.set_font('Arial', '', 8)
            pdf.cell(25, 5, 'Condición:', align='L')
            pdf.set_font('Arial', 'B', 8)
            pdf.cell(0, 5, condicion, ln=1, align='L')

            # Si es en cuotas, mostramos los detalles
            if condicion == "En Cuotas" and payment_details.get("num_cuotas"):
                pdf.set_font('Arial', '', 8)
                cuotas_texto = f"{payment_details.get('num_cuotas')} cuotas de S/ {payment_details.get('monto_cuota', '0.00')}"
                pdf.cell(25) # Sangría
                pdf.cell(0, 5, cuotas_texto, ln=1, align='L')

        metodo = payment_details.get("metodo")
        monto_pagado = payment_details.get("monto_pagado")
        if metodo and monto_pagado:
            pdf.set_font('Arial', '', 8)
            pdf.cell(25, 5, 'Pagado con:', align='L')
            pdf.set_font('Arial', 'B', 8)
            pdf.cell(0, 5, f"{metodo} - S/ {monto_pagado}", ln=1, align='L')
        pdf.ln(5)

        # --- MENSAJE FINAL DE AGRADECIMIENTO ---
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 5, '¡Gracias por su compra!', ln=1, align='C')
        
        final_output_path = f"{output_path}_ticket.pdf"
        pdf.output(final_output_path)
        return final_output_path

    except Exception as e:
        raise e