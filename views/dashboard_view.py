import tkinter as tk
import customtkinter as ctk
from repositories import PetCareService
from sound_manager import SoundManager

BG_MAIN = "#0f172a"
BG_CARD = "#1e293b"
BG_ITEM_CARD = "#172236"
BG_ITEM_HOVER = "#23334d"
BORDER_SUBTLE = "#334155"
TEAL_ACCENT = "#2dd4bf"
AMBER_PILL = "#fbbf24"
BLUE_PILL = "#38bdf8"
ROSE_PILL = "#f472b6"
RED_HOVER = "#dc2626"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color="transparent")
        self.app = app_ref

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)
        ctk.CTkLabel(header, text="Agenda Médica & Pacientes 🩺", font=("Segoe UI", 22, "bold"), text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(header, text="Panel de control operativo en tiempo real", font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(anchor="w")

        # KPIs
        cards_grid = ctk.CTkFrame(self, fg_color="transparent")
        cards_grid.grid(row=1, column=0, sticky="ew", pady=(0, 15), padx=5)
        cards_grid.grid_columnconfigure((0, 1, 2), weight=1)

        self.kpi_clientes = self._crear_kpi_card(cards_grid, 0, "Dueños Registrados", "0", "👥", TEAL_ACCENT)
        self.kpi_mascotas = self._crear_kpi_card(cards_grid, 1, "Pacientes / Pets", "0", "🐾", ROSE_PILL)
        self.kpi_citas = self._crear_kpi_card(cards_grid, 2, "Citas Agendadas", "0", "🗓️", AMBER_PILL)

        # Contenedor Tabla/Feed
        content_box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_SUBTLE)
        content_box.grid(row=2, column=0, sticky="nsew", padx=5)
        content_box.grid_columnconfigure(0, weight=1)
        content_box.grid_rowconfigure(1, weight=1)

        filter_bar = ctk.CTkFrame(content_box, fg_color="transparent")
        filter_bar.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 12))

        ctk.CTkLabel(filter_bar, text="🔍 Búsqueda:", font=("Segoe UI", 12, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=(0, 8))

        self.f_dueno = ctk.CTkEntry(filter_bar, placeholder_text="Dueño...", width=160, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.f_dueno.pack(side="left", padx=4)
        self.f_dueno.bind("<KeyRelease>", lambda e: self.cargar_datos())

        self.f_mascota = ctk.CTkEntry(filter_bar, placeholder_text="Mascota...", width=150, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.f_mascota.pack(side="left", padx=4)
        self.f_mascota.bind("<KeyRelease>", lambda e: self.cargar_datos())

        self.f_fecha = ctk.CTkEntry(filter_bar, placeholder_text="AAAA-MM-DD", width=140, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.f_fecha.pack(side="left", padx=4)
        self.f_fecha.bind("<KeyRelease>", lambda e: self.cargar_datos())

        btn_clear = ctk.CTkButton(filter_bar, text="Restablecer", width=95, corner_radius=10, fg_color="#334155", hover_color="#475569", command=self._limpiar_filtros)
        btn_clear.pack(side="left", padx=8)

        self.scroll_agenda = ctk.CTkScrollableFrame(content_box, fg_color="transparent", corner_radius=12)
        self.scroll_agenda.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

    def _crear_kpi_card(self, parent, col, title, init_val, icon, accent_color):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_SUBTLE)
        card.grid(row=0, column=col, padx=8, sticky="ew")
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=18, pady=(16, 2))
        ctk.CTkLabel(top_row, text=title, font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkLabel(top_row, text=icon, font=("Segoe UI", 16)).pack(side="right")
        lbl = ctk.CTkLabel(card, text=init_val, font=("Segoe UI", 28, "bold"), text_color=accent_color)
        lbl.pack(anchor="w", padx=18, pady=(0, 16))
        return lbl

    def cargar_datos(self):
        for widget in self.scroll_agenda.winfo_children():
            widget.destroy()

        c, m, ci = PetCareService.obtener_metricas()
        self.kpi_clientes.configure(text=str(c))
        self.kpi_mascotas.configure(text=str(m))
        self.kpi_citas.configure(text=str(ci))

        citas = PetCareService.buscar_agenda(self.f_dueno.get(), self.f_mascota.get(), self.f_fecha.get())
        if not citas:
            ctk.CTkLabel(self.scroll_agenda, text="No hay citas agendadas que coincidan.", font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(pady=50)
            return

        es_admin = self.app.usuario_activo and self.app.usuario_activo.get("rol") == "Administrador"

        for r in citas:
            cid = int(r["idCita"])
            fa, ha, ma = str(r["fechaCita"]), str(r["horaCita"]), str(r["nombreMascota"])

            card = ctk.CTkFrame(self.scroll_agenda, fg_color=BG_ITEM_CARD, corner_radius=14, border_width=1, border_color=BORDER_SUBTLE)
            card.pack(fill="x", pady=8, padx=6)
            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color=BG_ITEM_HOVER))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=BG_ITEM_CARD))

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=18, pady=14)

            col_izq = ctk.CTkFrame(inner, fg_color="transparent")
            col_izq.pack(side="left")

            ctk.CTkLabel(col_izq, text=f"🐾  {r['nombreMascota']}", font=("Segoe UI", 16, "bold"), text_color=TEXT_MAIN).pack(anchor="w")
            ctk.CTkLabel(col_izq, text=f"Dueño: {r['nomDueno']}", font=("Segoe UI", 13, "bold"), text_color=TEAL_ACCENT).pack(anchor="w", pady=(2, 1))
            ctk.CTkLabel(col_izq, text=f"Especie: {r['especie']}   |   Raza: {r['raza'] or 'N/A'}", font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(anchor="w")

            col_der = ctk.CTkFrame(inner, fg_color="transparent")
            col_der.pack(side="right")

            bf = ctk.CTkFrame(col_der, fg_color="#1e293b", corner_radius=10, border_width=1, border_color="#3b82f6")
            bf.pack(side="left", padx=4)
            ctk.CTkLabel(bf, text=f"📅  {r['fechaCita']}", font=("Segoe UI", 11, "bold"), text_color=BLUE_PILL).pack(padx=10, pady=6)

            bh = ctk.CTkFrame(col_der, fg_color="#1e293b", corner_radius=10, border_width=1, border_color="#f59e0b")
            bh.pack(side="left", padx=4)
            ctk.CTkLabel(bh, text=f"⏰  {r['horaCita']}", font=("Segoe UI", 11, "bold"), text_color=AMBER_PILL).pack(padx=10, pady=6)

            ctk.CTkButton(
                col_der, text="✏️ Editar", width=75, height=32, corner_radius=8, font=("Segoe UI", 11, "bold"),
                fg_color="#334155", hover_color="#475569", command=lambda i=cid, f=fa, h=ha, m=ma: self.app.abrir_modal_editar_cita(i, f, h, m)
            ).pack(side="left", padx=4)

            if es_admin:
                ctk.CTkButton(
                    col_der, text="🗑️", width=38, height=32, corner_radius=8, font=("Segoe UI", 12, "bold"),
                    fg_color="#7f1d1d", hover_color=RED_HOVER, command=lambda i=cid, m=ma: self.app.abrir_modal_eliminar_cita(i, m)
                ).pack(side="left", padx=4)

            # Clic derecho
            self._bind_context_menu(card, cid, fa, ha, ma, es_admin)

    def _bind_context_menu(self, widget, cid, fa, ha, ma, es_admin):
        def pop(e):
            SoundManager.reproducir("click")
            menu = tk.Menu(self, tearoff=0, bg="#1e293b", fg="#ffffff", activebackground="#0284c7", activeforeground="#ffffff", font=("Segoe UI", 10))
            menu.add_command(label=f"✏️ Editar Horario ({ma})", command=lambda: self.app.abrir_modal_editar_cita(cid, fa, ha, ma))
            if es_admin:
                menu.add_separator()
                menu.add_command(label="🗑️ Eliminar Cita", command=lambda: self.app.abrir_modal_eliminar_cita(cid, ma))
            menu.post(e.x_root, e.y_root)
        widget.bind("<Button-3>", pop)

    def _limpiar_filtros(self):
        SoundManager.reproducir("click")
        self.f_dueno.delete(0, "end")
        self.f_mascota.delete(0, "end")
        self.f_fecha.delete(0, "end")
        self.cargar_datos()