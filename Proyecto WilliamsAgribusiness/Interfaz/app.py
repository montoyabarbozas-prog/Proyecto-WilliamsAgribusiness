import customtkinter as ctk
from interfaz.config import MODULES
from interfaz.vistas.dashboard import DashboardView
from interfaz.vistas.modulo import ModuleView


class WilliamsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("William's Agribusiness | Sistema de gestión")

        # Ajusta el tamaño inicial al espacio disponible en la pantalla.
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        window_w = min(1180, max(760, screen_w - 80))
        window_h = min(760, max(520, screen_h - 100))
        self.geometry(f"{window_w}x{window_h}")
        self.minsize(700, 480)
        self.configure(fg_color='#F1F5F9')

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=205, corner_radius=0, fg_color='#14243A')
        self.sidebar.grid(row=0, column=0, sticky='nsew')
        self.sidebar.grid_propagate(False)

        self.main_area = ctk.CTkFrame(self, fg_color='#F1F5F9', corner_radius=0)
        self.main_area.grid(row=0, column=1, sticky='nsew', padx=12, pady=12)
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)

        self._build_sidebar()
        self._build_topbar()
        self.show_dashboard()

    def _build_sidebar(self):
        bottom = ctk.CTkFrame(self.sidebar, fg_color='#203650', corner_radius=10)
        bottom.pack(side='bottom', fill='x', padx=10, pady=10)
        ctk.CTkLabel(bottom, text='VERSIÓN DE INTERFAZ', font=ctk.CTkFont(size=9, weight='bold'), text_color='#9FB3CC').pack(anchor='w', padx=10, pady=(8, 2))
        ctk.CTkLabel(bottom, text='Sin conexión a SQL Server', font=ctk.CTkFont(size=10), text_color='#FFFFFF').pack(anchor='w', padx=10, pady=(0, 8))

        brand = ctk.CTkFrame(self.sidebar, fg_color='transparent')
        brand.pack(fill='x', padx=15, pady=(16, 18))
        ctk.CTkLabel(brand, text='🌿', font=ctk.CTkFont(size=27)).pack(anchor='w')
        ctk.CTkLabel(brand, text="WILLIAM'S", font=ctk.CTkFont(size=18, weight='bold'), text_color='#FFFFFF').pack(anchor='w', pady=(4, 0))
        ctk.CTkLabel(brand, text='AGRIBUSINESS', font=ctk.CTkFont(size=10, weight='bold'), text_color='#8FA7C4').pack(anchor='w')
        ctk.CTkLabel(self.sidebar, text='MENÚ PRINCIPAL', font=ctk.CTkFont(size=9, weight='bold'), text_color='#7890AE').pack(anchor='w', padx=17, pady=(0, 6))

        # Menú lateral azul fijo, sin barra de desplazamiento.
        self.nav_menu = ctk.CTkFrame(self.sidebar, fg_color='transparent', corner_radius=0)
        self.nav_menu.pack(fill='both', expand=True, padx=6, pady=(0, 6))
        self._nav_button('⌂', 'Panel principal', self.show_dashboard)
        for name, cfg in MODULES.items():
            self._nav_button(cfg['icon'], name, lambda n=name: self.show_module(n))

    def _nav_button(self, icon, label, command):
        ctk.CTkButton(
            self.nav_menu, text=f'{icon}   {label}', command=command,
            anchor='w', height=40, corner_radius=8, fg_color='transparent',
            hover_color='#263D59', text_color='#E6EDF5',
            font=ctk.CTkFont(size=11)
        ).pack(fill='x', padx=3, pady=2)

    def _build_topbar(self):
        top = ctk.CTkFrame(self.main_area, fg_color='transparent')
        top.grid(row=0, column=0, sticky='ew', pady=(0, 8))
        ctk.CTkLabel(top, text='Sistema de administración', font=ctk.CTkFont(size=12, weight='bold'), text_color='#475569').pack(side='left')
        ctk.CTkLabel(top, text="William's Agribusiness  •  SQL Server (pendiente)", font=ctk.CTkFont(size=10), text_color='#64748B').pack(side='right')

    def _clear_content(self):
        for widget in self.main_area.winfo_children():
            if str(widget.grid_info().get('row')) == '1':
                widget.destroy()

    def show_dashboard(self):
        self._clear_content()
        DashboardView(self.main_area, self.show_module).grid(row=1, column=0, sticky='nsew')

    def show_module(self, module_name):
        self._clear_content()
        ModuleView(self.main_area, module_name, MODULES[module_name]).grid(row=1, column=0, sticky='nsew')
