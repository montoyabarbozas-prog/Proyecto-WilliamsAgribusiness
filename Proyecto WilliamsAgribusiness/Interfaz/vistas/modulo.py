
from tkinter import messagebox
import customtkinter as ctk

from CapaNegocios.InventarioNegocio import InventarioNegocio


class ModuleView(ctk.CTkFrame):

    def __init__(self, master, module_name, config):
        super().__init__(master, fg_color='transparent')

        self.module_name = module_name
        self.config_data = config
        self.selected_table = list(config['tables'])[0]
        self.entries = {}

        if module_name.lower() == "inventario":
            self._build_inventario()
        else:
            self._build()

    # ==================================================
    # MODULO INVENTARIO
    # ==================================================

    def _build_inventario(self):

        ctk.CTkLabel(
            self,
            text="Inventario",
            font=ctk.CTkFont(size=27, weight="bold"),
            text_color="#172B4D"
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            self,
            text="Consulta y administración de existencias y movimientos.",
            font=ctk.CTkFont(size=13),
            text_color="#64748B"
        ).pack(anchor="w", pady=(0, 18))

        selector = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=12)
        selector.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(
            selector,
            text="Operación:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#334155"
        ).pack(side="left", padx=(15, 8), pady=12)

        self.operacion = ctk.CTkOptionMenu(
            selector,
            values=[
                "Consultar inventario",
                "Registrar entrada",
                "Registrar salida",
                "Registrar ajuste",
                "Consultar movimientos"
            ],
            command=self._cambiar_operacion,
            width=230
        )
        self.operacion.pack(side="left", pady=10)

        self.content = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.content.pack(fill="both", expand=True)

        self._cambiar_operacion("Consultar inventario")

    def _cambiar_operacion(self, operacion):

        for widget in self.content.winfo_children():
            widget.destroy()

        self.entries = {}

        titulo = ctk.CTkLabel(
            self.content,
            text=operacion,
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#172B4D"
        )
        titulo.pack(anchor="w", padx=18, pady=(16, 10))

        if operacion == "Consultar inventario":
            self._formulario_consulta()

        elif operacion == "Consultar movimientos":
            self._formulario_movimientos()

        else:
            self._formulario_movimiento(operacion)

    def _crear_campo(self, contenedor, nombre, placeholder):

        ctk.CTkLabel(
            contenedor,
            text=nombre,
            font=ctk.CTkFont(size=12),
            text_color="#475569"
        ).pack(anchor="w", padx=18, pady=(7, 2))

        entrada = ctk.CTkEntry(
            contenedor,
            placeholder_text=placeholder,
            height=35,
            width=300
        )
        entrada.pack(anchor="w", padx=18, pady=(0, 5))

        self.entries[nombre] = entrada

    def _obtener_id(self, nombre):

        valor = self.entries[nombre].get().strip()

        if not valor:
            return None

        try:
            numero = int(valor)
            if numero <= 0:
                raise ValueError
            return numero
        except ValueError:
            raise ValueError(f"{nombre} debe ser un número entero positivo.")

    def _formulario_consulta(self):

        self._crear_campo(
            self.content,
            "ID Producto",
            "Dejar vacío para consultar todos"
        )

        self._crear_campo(
            self.content,
            "ID Cultivo",
            "Dejar vacío para consultar todos"
        )

        ctk.CTkButton(
            self.content,
            text="Consultar inventario",
            command=self._consultar_inventario
        ).pack(anchor="w", padx=18, pady=12)

        self._crear_resultados()

        self._consultar_inventario()

    def _consultar_inventario(self):

        try:
            id_producto = self._obtener_id("ID Producto")
            id_cultivo = self._obtener_id("ID Cultivo")

            datos = InventarioNegocio.consultar_inventario(
                id_producto,
                id_cultivo
            )

            self._mostrar_resultados(datos)

        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _formulario_movimiento(self, operacion):

        self._crear_campo(
            self.content,
            "ID Inventario",
            "Ingrese el ID del inventario"
        )

        self._crear_campo(
            self.content,
            "Cantidad",
            "Ingrese la cantidad"
        )

        self._crear_campo(
            self.content,
            "Motivo",
            "Motivo del movimiento"
        )

        self._crear_campo(
            self.content,
            "Referencia",
            "Referencia opcional"
        )

        self._crear_campo(
            self.content,
            "Observaciones",
            "Observaciones opcionales"
        )

        ctk.CTkButton(
            self.content,
            text=operacion,
            command=lambda: self._ejecutar_movimiento(operacion)
        ).pack(anchor="w", padx=18, pady=15)

    def _ejecutar_movimiento(self, operacion):

        try:
            id_inventario = self._obtener_id("ID Inventario")

            cantidad_texto = self.entries["Cantidad"].get().strip()

            try:
                cantidad = float(cantidad_texto)
            except ValueError:
                raise ValueError("La cantidad debe ser numérica.")

            motivo = self.entries["Motivo"].get().strip()
            referencia = self.entries["Referencia"].get().strip() or None
            observaciones = self.entries["Observaciones"].get().strip() or None

            if operacion == "Registrar entrada":

                InventarioNegocio.registrar_entrada(
                    id_inventario,
                    cantidad,
                    motivo,
                    referencia,
                    observaciones
                )

            elif operacion == "Registrar salida":

                InventarioNegocio.registrar_salida(
                    id_inventario,
                    cantidad,
                    motivo,
                    referencia,
                    observaciones
                )

            elif operacion == "Registrar ajuste":

                InventarioNegocio.registrar_ajuste(
                    id_inventario,
                    cantidad,
                    motivo,
                    referencia,
                    observaciones
                )

            messagebox.showinfo(
                "Operación exitosa",
                "El movimiento se registró correctamente."
            )

            self._cambiar_operacion("Consultar inventario")

        except Exception as error:
            messagebox.showerror("Error al registrar", str(error))

    def _formulario_movimientos(self):

        self._crear_campo(
            self.content,
            "ID Inventario",
            "Dejar vacío para consultar todos"
        )

        self._crear_campo(
            self.content,
            "Fecha inicio",
            "AAAA-MM-DD (opcional)"
        )

        self._crear_campo(
            self.content,
            "Fecha fin",
            "AAAA-MM-DD (opcional)"
        )

        ctk.CTkButton(
            self.content,
            text="Consultar movimientos",
            command=self._consultar_movimientos
        ).pack(anchor="w", padx=18, pady=12)

        self._crear_resultados()

    def _consultar_movimientos(self):

        try:
            id_inventario = self._obtener_id("ID Inventario")

            inicio = self.entries["Fecha inicio"].get().strip() or None
            fin = self.entries["Fecha fin"].get().strip() or None

            datos = InventarioNegocio.consultar_movimientos(
                id_inventario,
                inicio,
                fin
            )

            self._mostrar_resultados(datos)

        except Exception as error:
            messagebox.showerror("Error", str(error))

    def _crear_resultados(self):

        self.resultados = ctk.CTkTextbox(
            self.content,
            height=220,
            font=ctk.CTkFont(size=11)
        )
        self.resultados.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(5, 15)
        )

    def _mostrar_resultados(self, datos):

        self.resultados.configure(state="normal")
        self.resultados.delete("1.0", "end")

        if not datos:
            self.resultados.insert("end", "No se encontraron registros.")
        else:
            for registro in datos:
                for campo, valor in registro.items():
                    self.resultados.insert(
                        "end",
                        f"{campo}: {valor}\n"
                    )
                self.resultados.insert("end", "-" * 45 + "\n")

        self.resultados.configure(state="disabled")

    # ==================================================
    # RESTO DE MODULOS: INTERFAZ DE DEMOSTRACION
    # ==================================================

    def _build(self):

        ctk.CTkLabel(
            self,
            text=self.module_name,
            font=ctk.CTkFont(size=27, weight='bold'),
            text_color='#172B4D'
        ).pack(anchor='w', pady=(4, 0))

        ctk.CTkLabel(
            self,
            text=self.config_data['description'],
            font=ctk.CTkFont(size=13),
            text_color='#64748B'
        ).pack(anchor='w', pady=(0, 18))

        selector = ctk.CTkFrame(self, fg_color='#FFFFFF', corner_radius=12)
        selector.pack(fill='x', pady=(0, 14))

        ctk.CTkLabel(
            selector,
            text='Tabla:',
            font=ctk.CTkFont(size=12, weight='bold'),
            text_color='#334155'
        ).pack(side='left', padx=(15, 8), pady=12)

        self.table_menu = ctk.CTkOptionMenu(
            selector,
            values=list(self.config_data['tables']),
            command=self.change_table,
            width=230
        )
        self.table_menu.pack(side='left', pady=10)

        self.content = ctk.CTkFrame(
            self,
            fg_color='#FFFFFF',
            corner_radius=12,
            border_width=1,
            border_color='#E2E8F0'
        )
        self.content.pack(fill='both', expand=True)

        self._render_table()

    def change_table(self, table_name):

        self.selected_table = table_name
        self._render_table()

    def _render_table(self):

        for widget in self.content.winfo_children():
            widget.destroy()

        self.entries = {}

        fields = self.config_data['tables'][self.selected_table]

        top = ctk.CTkFrame(self.content, fg_color='transparent')
        top.pack(fill='x', padx=18, pady=(16, 8))

        ctk.CTkLabel(
            top,
            text=f'Administrar {self.selected_table}',
            font=ctk.CTkFont(size=18, weight='bold'),
            text_color='#172B4D'
        ).pack(side='left')

        search = ctk.CTkFrame(self.content, fg_color='transparent')
        search.pack(fill='x', padx=18, pady=(4, 12))

        self.search_entry = ctk.CTkEntry(
            search,
            placeholder_text='Buscar (demostración)...',
            height=36
        )
        self.search_entry.pack(
            side='left',
            fill='x',
            expand=True,
            padx=(0, 8)
        )

        ctk.CTkButton(
            search,
            text='Buscar',
            width=95,
            height=36,
            command=self._not_connected
        ).pack(side='left')

        body = ctk.CTkFrame(self.content, fg_color='transparent')
        body.pack(fill='both', expand=True, padx=18, pady=(0, 12))

        form = ctk.CTkFrame(body, fg_color='#F8FAFC', corner_radius=10)
        form.pack(side='left', fill='y', padx=(0, 14))

        ctk.CTkLabel(
            form,
            text='Datos del registro',
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color='#334155'
        ).pack(anchor='w', padx=12, pady=(12, 8))

        scroll = ctk.CTkScrollableFrame(
            form,
            width=230,
            height=350,
            fg_color='transparent'
        )
        scroll.pack(fill='both', expand=True, padx=8, pady=(0, 8))

        for field in fields:

            ctk.CTkLabel(
                scroll,
                text=field,
                font=ctk.CTkFont(size=11),
                text_color='#475569'
            ).pack(anchor='w', padx=4, pady=(5, 2))

            entry = ctk.CTkEntry(
                scroll,
                placeholder_text=f'Ingrese {field}',
                width=205,
                height=32
            )
            entry.pack(padx=4, pady=(0, 3))
            self.entries[field] = entry

        actions = ctk.CTkFrame(form, fg_color='transparent')
        actions.pack(fill='x', padx=10, pady=(0, 10))

        for label in ('Nuevo', 'Guardar', 'Actualizar', 'Eliminar'):

            ctk.CTkButton(
                actions,
                text=label,
                height=30,
                command=self._not_connected
            ).pack(fill='x', pady=3)

        listing = ctk.CTkFrame(
            body,
            fg_color='#FFFFFF',
            corner_radius=10,
            border_width=1,
            border_color='#E2E8F0'
        )
        listing.pack(side='left', fill='both', expand=True)

        ctk.CTkLabel(
            listing,
            text='Registros',
            font=ctk.CTkFont(size=14, weight='bold'),
            text_color='#334155'
        ).pack(anchor='w', padx=14, pady=(12, 5))

        ctk.CTkLabel(
            listing,
            text='La tabla de resultados aparecerá aquí al conectar SQL Server.',
            font=ctk.CTkFont(size=12),
            text_color='#64748B',
            wraplength=430
        ).pack(anchor='w', padx=14, pady=(4, 10))

        head = ctk.CTkFrame(listing, fg_color='#EFF4FA', corner_radius=6)
        head.pack(fill='x', padx=12, pady=5)

        for field in fields[:4]:

            ctk.CTkLabel(
                head,
                text=field,
                font=ctk.CTkFont(size=10, weight='bold'),
                text_color='#334155'
            ).pack(side='left', padx=8, pady=9)

        ctk.CTkLabel(
            listing,
            text='Sin datos: módulo todavía no conectado.',
            font=ctk.CTkFont(size=11),
            text_color='#94A3B8'
        ).pack(anchor='w', padx=14, pady=12)

    def _not_connected(self):

        messagebox.showinfo(
            'Interfaz en desarrollo',
            'Este módulo todavía no está conectado a SQL Server.'
        )

