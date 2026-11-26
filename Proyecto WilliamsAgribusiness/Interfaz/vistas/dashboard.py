import customtkinter as ctk


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, navigate):
        super().__init__(master, fg_color='transparent')
        self.navigate = navigate
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Todo el panel principal se puede desplazar en pantallas pequeñas.
        scroll = ctk.CTkScrollableFrame(self, fg_color='transparent', corner_radius=0)
        scroll.grid(row=0, column=0, sticky='nsew')
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scroll, text='Panel principal', font=ctk.CTkFont(size=25, weight='bold'), text_color='#172B4D').pack(anchor='w', pady=(5, 4))
        ctk.CTkLabel(scroll, text="Sistema de gestión agrícola · William's Agribusiness", font=ctk.CTkFont(size=12), text_color='#64748B').pack(anchor='w', pady=(0, 16))

        cards = ctk.CTkFrame(scroll, fg_color='transparent')
        cards.pack(fill='x')
        cards.grid_columnconfigure((0, 1, 2), weight=1, uniform='stats')
        for col, (value, label, bg, fg) in enumerate([
            ('14', 'Tablas contempladas', '#E8F1FF', '#2457A6'),
            ('5', 'Módulos del sistema', '#E8F7EF', '#18794E'),
            ('0', 'Conexión a base de datos', '#FFF4E5', '#A15C07')
        ]):
            card = ctk.CTkFrame(cards, fg_color=bg, corner_radius=12)
            card.grid(row=0, column=col, sticky='nsew', padx=(0, 8), pady=3)
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=23, weight='bold'), text_color=fg).pack(anchor='w', padx=12, pady=(11, 0))
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=10), text_color=fg, wraplength=115).pack(anchor='w', padx=12, pady=(0, 11))

        ctk.CTkLabel(scroll, text='Accesos a los módulos', font=ctk.CTkFont(size=17, weight='bold'), text_color='#172B4D').pack(anchor='w', pady=(22, 10))
        grid = ctk.CTkFrame(scroll, fg_color='transparent')
        grid.pack(fill='x')
        grid.grid_columnconfigure((0, 1), weight=1, uniform='modules')
        options = [
            ('👥', 'Clientes', 'Segmentos, clientes y contactos'),
            ('📄', 'Contratos', 'Contratos y productos pactados'),
            ('🌱', 'Producción', 'Fincas, lotes y cultivos'),
            ('📦', 'Inventario', 'Productos, existencias y movimientos'),
            ('🚚', 'Ventas y entregas', 'Ventas, detalles y entregas')
        ]
        for i, (icon, name, desc) in enumerate(options):
            row, col = divmod(i, 2)
            card = ctk.CTkFrame(grid, fg_color='#FFFFFF', corner_radius=12, border_width=1, border_color='#E2E8F0')
            card.grid(row=row, column=col, sticky='nsew', padx=(0, 8), pady=(0, 9))
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=22)).pack(anchor='w', padx=13, pady=(10, 2))
            ctk.CTkLabel(card, text=name, font=ctk.CTkFont(size=14, weight='bold'), text_color='#172B4D').pack(anchor='w', padx=13)
            ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=10), text_color='#64748B', wraplength=210, justify='left').pack(anchor='w', padx=13, pady=(2, 8))
            ctk.CTkButton(card, text='Abrir módulo', height=29, command=lambda n=name: self.navigate(n)).pack(anchor='w', padx=13, pady=(0, 11))
