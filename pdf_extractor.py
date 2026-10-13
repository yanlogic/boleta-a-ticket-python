# pdf_extractor.py (VERSIÓN FINAL CON IF/ELSE PARA CÓDIGO DE ITEM)
import fitz
import re

def extract_data_from_pdf(pdf_path):
    """
    Extrae datos usando una lógica IF/ELSE global para el DNI y otra para el código de item.
    """
    print("\n" + "="*25 + " INICIANDO DEPURACIÓN " + "="*25)
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()

        print("\n--- PASO 1: TEXTO COMPLETO EXTRAÍDO DEL PDF ---")
        print(text)
        print("------------------------------------------------\n")
        
        extracted_data = {}

        # --- DECISIÓN GLOBAL: ¿EXISTE EL CAMPO DNI? ---
        if re.search(r"\bDNI\b\s*:", text, re.IGNORECASE):
            print("--- DECISIÓN: Se detectó un campo DNI. Usando PATRONES_CON_DNI. ---")
            
            PATTERNS_CON_DNI = {
                "ruc": r"RUC\s*:\s*(\d{11})",
                "tipo_documento": r"(BOLETA DE VENTA ELECTRONICA|FACTURA ELECTRONICA)",
                "numero_documento": r"([A-Z0-9]{4}-\d+)",
                "fecha_emision": r"Fecha de Emisión\s*:\s*(\d{2}/\d{2}/\d{4})",
                "cliente_nombre": r"Señor\(es\)\s*:\s*(.*?)(?=\s*DNI)",
                "cliente_ruc_dni": r"DNI\s*:\s*(.*?)(?=\s*Tipo de Moneda)",
                "op_gravada": r"Op\.\s*Gravada\s*:\s*S/.*?(\d+\.\d{2})",
                "igv": r"IGV\s*:\s*S/.*?(\d+\.\d{2})",
                "total": r"(?:Importe\sTotal|TOTAL)\s*:\s*S/.*?(\d+\.\d{2})",
                "total_letras": r"SON:\s*(.*?)(?=\s*\(\*\)\s*Sin impuestos)",
                "items_block": r"Importe de Venta\(\*\*\)\n(.+?)(?=\nSON:)"
            }
            
            for key, pattern in PATTERNS_CON_DNI.items():
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    extracted_data[key] = ' '.join(match.groups()[-1].strip().split())
                else:
                    extracted_data[key] = None
        
        else:
            print("--- DECISIÓN: No se detectó un campo DNI. Usando PATRONES_SIN_DNI. ---")

            PATRONES_SIN_DNI = {
                "ruc": r"RUC\s*:\s*(\d{11})",
                "tipo_documento": r"(BOLETA DE VENTA ELECTRONICA|FACTURA ELECTRONICA)",
                "numero_documento": r"([A-Z0-9]{4}-\d+)",
                "fecha_emision": r"Fecha de Emisión\s*:\s*(\d{2}/\d{2}/\d{4})",
                "cliente_nombre": r"Señor\(es\)\s*:\s*(.*?)(?=\s*Tipo de Moneda)",
                "op_gravada": r"Op\.\s*Gravada\s*:\s*S/.*?(\d+\.\d{2})",
                "igv": r"IGV\s*:\s*S/.*?(\d+\.\d{2})",
                "total": r"(?:Importe\sTotal|TOTAL)\s*:\s*S/.*?(\d+\.\d{2})",
                "total_letras": r"SON:\s*(.*?)(?=\s*\(\*\)\s*Sin impuestos)",
                "items_block": r"Importe de Venta\(\*\*\)\n(.+?)(?=\nSON:)"
            }

            for key, pattern in PATRONES_SIN_DNI.items():
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    extracted_data[key] = ' '.join(match.groups()[-1].strip().split())
                else:
                    extracted_data[key] = None
            
            extracted_data['cliente_ruc_dni'] = "Ninguno"
        
        # --- PASO FINAL: PROCESANDO DETALLE DE ITEMS (CON LÓGICA IF/ELSE PARA CÓDIGO) ---
        print("\n--- PASO FINAL: PROCESANDO DETALLE DE ITEMS ---")
        items_block = extracted_data.get("items_block")
        if items_block:
            flat_text = ' '.join(items_block.split())
            print(f"\nTexto del bloque de items a analizar:\n'{flat_text}'")
            
            item_match = None
            
            # --- DECISIÓN PARA ITEMS: ¿EXISTE UN CÓDIGO NUMÉRICO? ---
            if re.search(r"UNIDAD\s+\d+\s+", flat_text, re.IGNORECASE):
                print("   -> Lógica de Items: Se detectó un CÓDIGO numérico después de 'UNIDAD'.")
                # SI HAY CÓDIGO, usamos una regla que lo espera y lo omite
                item_regex = r"(\d+)\.\d+\s+(\w+)\s+\d+\s+(.*?)\s+(\d+\.\d+)\s+[\d\.]+"
                print(f"    usando la regla (con código): {item_regex}")
                item_match = re.search(item_regex, flat_text)
            else:
                print("   -> Lógica de Items: No se detectó código. Usando regla estándar.")
                # SI NO HAY CÓDIGO, usamos la regla que no lo espera
                item_regex = r"(\d+)\.\d+\s+(\w+)\s+(.*?)\s+(\d+\.\d+)\s+[\d\.]+"
                print(f"    usando la regla (sin código): {item_regex}")
                item_match = re.search(item_regex, flat_text)

            # --- PROCESAMIENTO DEL RESULTADO (IDÉNTICO PARA AMBOS CASOS) ---
            if item_match:
                extracted_data['cantidad'] = item_match.group(1).strip()
                extracted_data['unidad_medida'] = item_match.group(2).strip()
                extracted_data['descripcion'] = item_match.group(3).strip()
                p_unitario_raw = item_match.group(4).strip()
                try:
                    p_unitario_float = float(p_unitario_raw)
                    p_unitario_rounded = round(p_unitario_float, 3)
                    p_unitario_final = f"{p_unitario_rounded:.3f}"
                    extracted_data['valor_unitario'] = p_unitario_final
                except ValueError:
                    extracted_data['valor_unitario'] = p_unitario_raw
                print(f"   ✅ ÉXITO [Items]. Se extrajeron todos los detalles.")
            else:
                print("   ❌ FALLÓ. No se encontraron los detalles de items con ninguna de las reglas.")
        else:
            print("   ⚠️ No se encontró el 'items_block' para analizar.")
        
        print("\n------------------------------------------------")
        print("--- DICCIONARIO FINAL DE DATOS ---")
        print(extracted_data)
        print("="*24 + " FIN DE LA DEPURACIÓN " + "="*25 + "\n")
            
        return extracted_data

    except Exception as e:
        print(f"Error CRÍTICO durante la depuración: {e}")
        return None