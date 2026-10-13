# main.py (versión con botones)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys # para la función de abrir archivo
import subprocess # para la función de abrir archivo

from pdf_extractor import extract_data_from_pdf
from ticket_generator import create_ticket

# --- Configuraciones ---
APP_TITLE = "Convertidor de Boletas a Ticket"

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("600x550")
        
        # Variables para almacenar las rutas de los archivos
        self.pdf_path = tk.StringVar()
        self.logo_path = tk.StringVar()

        self.condicion_pago = tk.StringVar(value="Al Contado") # Valor por defecto
        self.num_cuotas = tk.StringVar()
        self.monto_cuota = tk.StringVar()
        self.metodo_pago = tk.StringVar(value="Efectivo") # Valor por defecto
        self.monto_pagado = tk.StringVar()

        # Estilo
        style = ttk.Style(self)
        style.configure("TLabel", padding=5, font=('Helvetica', 10))
        style.configure("TButton", padding=10, font=('Helvetica', 10, 'bold'))
        style.configure("TFrame", padding=20)

        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill="both")
        
        # --- SECCIÓN DE SELECCIÓN DE PDF ---
        pdf_frame = ttk.LabelFrame(main_frame, text="Paso 1: Seleccionar Comprobante")
        pdf_frame.pack(fill="x", padx=10, pady=10)

        self.pdf_label = ttk.Label(pdf_frame, text="Ningún archivo seleccionado")
        self.pdf_label.pack(side="left", fill="x", expand=True, padx=10)
        
        pdf_button = ttk.Button(pdf_frame, text="Buscar PDF...", command=self.select_pdf)
        pdf_button.pack(side="right")

        # --- SECCIÓN DE SELECCIÓN DE LOGO ---
        logo_frame = ttk.LabelFrame(main_frame, text="Paso 2: Seleccionar Logo (Opcional)")
        logo_frame.pack(fill="x", padx=10, pady=10)
        
        self.logo_label = ttk.Label(logo_frame, text="Ningún logo seleccionado")
        self.logo_label.pack(side="left", fill="x", expand=True, padx=10)
        
        logo_button = ttk.Button(logo_frame, text="Buscar Logo...", command=self.select_logo)
        logo_button.pack(side="right")

                # --- SECCIÓN NUEVA: CONDICIÓN DE PAGO ---
        condicion_frame = ttk.LabelFrame(main_frame, text="Paso 3: Condición de Pago")
        condicion_frame.pack(fill="x", padx=10, pady=10)
        
        condicion_combo = ttk.Combobox(
            condicion_frame,
            textvariable=self.condicion_pago,
            values=["Al Contado", "En Cuotas"],
            state="readonly"
        )
        condicion_combo.pack(pady=5)
        condicion_combo.bind("<<ComboboxSelected>>", self.toggle_cuotas_fields)

        # --- SECCIÓN NUEVA Y CONDICIONAL: DETALLES DE CUOTAS ---
        # Este frame se mostrará u ocultará según la selección
        self.cuotas_frame = ttk.Frame(main_frame)
        
        ttk.Label(self.cuotas_frame, text="Número de Cuotas:").grid(row=0, column=0, sticky="w", padx=5)
        cuotas_entry = ttk.Entry(self.cuotas_frame, textvariable=self.num_cuotas)
        cuotas_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(self.cuotas_frame, text="Monto por Cuota S/:").grid(row=1, column=0, sticky="w", padx=5)
        monto_cuota_entry = ttk.Entry(self.cuotas_frame, textvariable=self.monto_cuota)
        monto_cuota_entry.grid(row=1, column=1, sticky="ew", padx=5)
        self.cuotas_frame.columnconfigure(1, weight=1) # Para que la casilla se expanda

        # --- SECCIÓN NUEVA: MÉTODO DE PAGO ---
        metodo_frame = ttk.LabelFrame(main_frame, text="Paso 4: Método de Pago")
        metodo_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Combobox(
            metodo_frame,
            textvariable=self.metodo_pago,
            values=["Efectivo", "Yape", "Plin", "Transferencia"],
            state="readonly"
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Label(metodo_frame, text="Monto Pagado S/:").grid(row=0, column=1, padx=5)
        ttk.Entry(metodo_frame, textvariable=self.monto_pagado).grid(row=0, column=2, padx=5)
        
        # --- SECCIÓN DE ACCIÓN ---
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(pady=20)
        
        convert_button = ttk.Button(action_frame, text="CONVERTIR A TICKET", command=self.process_conversion)
        convert_button.pack()
        
        # --- BARRA DE ESTADO ---
        self.status_label = ttk.Label(self, text="Listo para convertir.", anchor="w", relief="sunken")
        self.status_label.pack(side="bottom", fill="x", ipady=5)

    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona un archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if file_path:
            self.pdf_path.set(file_path)
            self.pdf_label.config(text=os.path.basename(file_path))
            self.status_label.config(text="PDF seleccionado. Listo para el siguiente paso.")

    def select_logo(self):
        file_path = filedialog.askopenfilename(
            title="Selecciona una imagen para el logo",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            self.logo_path.set(file_path)
            self.logo_label.config(text=os.path.basename(file_path))
            self.status_label.config(text="Logo seleccionado.")

    def process_conversion(self):
        pdf_file = self.pdf_path.get()
        if not pdf_file:
            messagebox.showerror("Error", "Por favor, selecciona primero un archivo PDF.")
            return

        self.status_label.config(text=f"Procesando: {os.path.basename(pdf_file)}...")
        self.update_idletasks()
        
        try:
            # 1. Extraer datos
            extracted_data = extract_data_from_pdf(pdf_file)
            if not extracted_data or not extracted_data.get('ruc'):
                raise ValueError("No se pudieron extraer datos válidos del PDF. Asegúrate de que es un comprobante de la SUNAT.")

            # 2. Definir ruta de salida
            output_dir = os.path.dirname(pdf_file)
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_path = os.path.join(output_dir, base_name)
            
                        # --- NUEVO: RECOLECTAR DATOS DE PAGO DE LA INTERFAZ ---
            payment_details = {
                "condicion": self.condicion_pago.get(),
                "num_cuotas": self.num_cuotas.get(),
                "monto_cuota": self.monto_cuota.get(),
                "metodo": self.metodo_pago.get(),
                "monto_pagado": self.monto_pagado.get()
            }

            logo_file = self.logo_path.get() or None
            
            # --- MODIFICADO: PASAMOS LOS NUEVOS DATOS AL GENERADOR ---
            ticket_file = create_ticket(extracted_data, logo_file, payment_details, output_path)
            
            # 4. Mostrar resultado
            messagebox.showinfo("Éxito", f"¡Ticket generado con éxito!\nGuardado como: {os.path.basename(ticket_file)}")
            self.status_label.config(text="Conversión completada. Listo para un nuevo archivo.")
            self.open_file(ticket_file)

        except Exception as e:
            # ¡Aquí está la magia! Mostramos el error detallado.
            messagebox.showerror("Ocurrió un Error", f"No se pudo completar la operación:\n\n{e}")
            self.status_label.config(text="Error. Inténtalo de nuevo.")

                # --- FUNCIÓN NUEVA: PARA MOSTRAR/OCULTAR CAMPOS DE CUOTAS ---
    def toggle_cuotas_fields(self, event=None):
        if self.condicion_pago.get() == "En Cuotas":
            self.cuotas_frame.pack(fill="x", padx=30, pady=5) # Lo mostramos
        else:
            self.cuotas_frame.pack_forget() # Lo ocultamos
            
    def open_file(self, path):
        """Abre un archivo con el programa predeterminado del sistema operativo."""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            else:
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, path])
        except Exception as e:
            print(f"No se pudo abrir el archivo automáticamente: {e}")


if __name__ == '__main__':
    app = App()
    app.mainloop()