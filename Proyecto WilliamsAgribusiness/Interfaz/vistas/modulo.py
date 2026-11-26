from tkinter import messagebox
import customtkinter as ctk

class ModuleView(ctk.CTkFrame):
    """Pantalla reutilizable para mostrar las tablas y formularios de cada módulo."""
    def __init__(self, master, module_name, config):
        super().__init__(master, fg_color='transparent')
        self.module_name = module_name
        self.config_data = config
        self.selected_table = list(config['tables'])[0]
        self.entries = {}
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=self.module_name, font=ctk.CTkFont(size=27, weight='bold'), text_color='#172B4D').pack(anchor='w', pady=(4, 0))
        ctk.CTkLabel(self, text=self.config_data['description'], font=ctk.CTkFont(size=13), text_color='#64748B').pack(anchor='w', pady=(0, 18))
        selector = ctk.CTkFrame(self, fg_color='#FFFFFF', corner_radius=12); selector.pack(fill='x', pady=(0, 14))
        ctk.CTkLabel(selector, text='Tabla:', font=ctk.CTkFont(size=12, weight='bold'), text_color='#334155').pack(side='left', padx=(15, 8), pady=12)
        self.table_menu = ctk.CTkOptionMenu(selector, values=list(self.config_data['tables']), command=self.change_table, width=230); self.table_menu.pack(side='left', pady=10)
        self.content = ctk.CTkFrame(self, fg_color='#FFFFFF', corner_radius=12, border_width=1, border_color='#E2E8F0'); self.content.pack(fill='both', expand=True)
        self._render_table()

    def change_table(self, table_name):
        self.selected_table = table_name
        self._render_table()

    def _render_table(self):
        for widget in self.content.winfo_children(): widget.destroy()
        self.entries = {}
        fields = self.config_data['tables'][self.selected_table]
        top = ctk.CTkFrame(self.content, fg_color='transparent'); top.pack(fill='x', padx=18, pady=(16, 8))
        ctk.CTkLabel(top, text=f'Administrar {self.selected_table}', font=ctk.CTkFont(size=18, weight='bold'), text_color='#172B4D').pack(side='left')
        search = ctk.CTkFrame(self.content, fg_color='transparent'); search.pack(fill='x', padx=18, pady=(4, 12))
        self.search_entry = ctk.CTkEntry(search, placeholder_text='Buscar (demostración)...', height=36); self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 8))
        ctk.CTkButton(search, text='Buscar', width=95, height=36, command=self._not_connected).pack(side='left')
        body = ctk.CTkFrame(self.content, fg_color='transparent'); body.pack(fill='both', expand=True, padx=18, pady=(0, 12))
        form = ctk.CTkFrame(body, fg_color='#F8FAFC', corner_radius=10); form.pack(side='left', fill='y', padx=(0, 14))
        ctk.CTkLabel(form, text='Datos del registro', font=ctk.CTkFont(size=14, weight='bold'), text_color='#334155').pack(anchor='w', padx=12, pady=(12, 8))
        scroll = ctk.CTkScrollableFrame(form, width=230, height=350, fg_color='transparent'); scroll.pack(fill='both', expand=True, padx=8, pady=(0, 8))
        for field in fields:
            ctk.CTkLabel(scroll, text=field, font=ctk.CTkFont(size=11), text_color='#475569').pack(anchor='w', padx=4, pady=(5, 2))
            entry = ctk.CTkEntry(scroll, placeholder_text=f'Ingrese {field}', width=205, height=32); entry.pack(padx=4, pady=(0, 3)); self.entries[field] = entry
        actions = ctk.CTkFrame(form, fg_color='transparent'); actions.pack(fill='x', padx=10, pady=(0, 10))
        for label in ('Nuevo', 'Guardar', 'Actualizar', 'Eliminar'):
            ctk.CTkButton(actions, text=label, height=30, command=self._not_connected).pack(fill='x', pady=3)
        listing = ctk.CTkFrame(body, fg_color='#FFFFFF', corner_radius=10, border_width=1, border_color='#E2E8F0'); listing.pack(side='left', fill='both', expand=True)
        ctk.CTkLabel(listing, text='Registros', font=ctk.CTkFont(size=14, weight='bold'), text_color='#334155').pack(anchor='w', padx=14, pady=(12, 5))
        ctk.CTkLabel(listing, text='La tabla de resultados aparecerá aquí al conectar SQL Server.', font=ctk.CTkFont(size=12), text_color='#64748B', wraplength=430).pack(anchor='w', padx=14, pady=(4, 10))
        head = ctk.CTkFrame(listing, fg_color='#EFF4FA', corner_radius=6); head.pack(fill='x', padx=12, pady=5)
        for field in fields[:4]: ctk.CTkLabel(head, text=field, font=ctk.CTkFont(size=10, weight='bold'), text_color='#334155').pack(side='left', padx=8, pady=9)
        ctk.CTkLabel(listing, text='Sin datos: todavía no hay conexión a la base de datos.', font=ctk.CTkFont(size=11), text_color='#94A3B8').pack(anchor='w', padx=14, pady=12)

    def _not_connected(self):
        messagebox.showinfo('Interfaz en desarrollo', 'Esta versión es únicamente visual. La conexión y las operaciones con SQL Server se agregarán en la siguiente etapa.')
