import calendar
from datetime import date, datetime, time
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from database import DatabaseManager
from repositories import PetCareRepository
from sound_manager import SoundManager
from pdf_generator import PDFReceiptGenerator

ctk.set_appearance_mode("light")

PALETTE = {
    "bg_main": "#F0FDF9",
    "sidebar": "#006D77",
    "sidebar_hover": "#008B8B",
    "card": "#FFFFFF",
    "primary": "#008B8B",
    "primary_hover": "#006666",
    "mint": "#10B981",
    "mint_hover": "#059669",
    "accent": "#FF7F50",
    "accent_hover": "#E06336",
    "danger": "#EF4444",
    "text_dark": "#1E293B",
    "text_muted": "#64748B",
}


# =========================================================================
# MODAL DE CALENDARIO INTERACTIVO (BLOQUEO DE DÍAS PASADOS)
# =========================================================================
class VetCalendarModal(ctk.CTkToplevel):
    def __init__(self, parent, fecha_inicial: str, on_date_selected):
        super().__init__(parent)
        self.title("Seleccionar Fecha de Cita")
        self.geometry("380x440")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_date_selected = on_date_selected
        self.hoy = date.today()

        try:
            d_init = datetime.strptime(fecha_inicial, "%Y-%m-%d").date()
            if d_init < self.hoy:
                d_init = self.hoy
        except Exception:
            d_init = self.hoy

        self.mes_actual = d_init.month
        self.anio_actual = d_init.year
        self.fecha_seleccionada = d_init

        self.configure(fg_color=PALETTE["bg_main"])
        self._construir_ui()
        self._dibujar_mes()

    def _construir_ui(self):
        header = ctk.CTkFrame(self, fg_color=PALETTE["sidebar"], corner_radius=12, height=55)
        header.pack(fill="x", padx=16, pady=(16, 10))
        header.pack_propagate(False)

        self.btn_prev = ctk.CTkButton(
            header, text="◀", width=34, height=34, fg_color="transparent",
            hover_color=PALETTE["sidebar_hover"], font=("Segoe UI", 13, "bold"),
            command=self._mes_anterior
        )
        self.btn_prev.pack(side="left", padx=8)

        self.lbl_mes_anio = ctk.CTkLabel(
            header, text="", font=("Segoe UI", 15, "bold"), text_color="#FFFFFF"
        )
        self.lbl_mes_anio.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(
            header, text="▶", width=34, height=34, fg_color="transparent",
            hover_color=PALETTE["sidebar_hover"], font=("Segoe UI", 13, "bold"),
            command=self._mes_siguiente
        )
        self.btn_next.pack(side="right", padx=8)

        self.grid_frame = ctk.CTkFrame(self, fg_color=PALETTE["card"], corner_radius=12)
        self.grid_frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        dias = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
        for col, dia in enumerate(dias):
            ctk.CTkLabel(
                self.grid_frame, text=dia, font=("Segoe UI", 11, "bold"),
                text_color=PALETTE["text_muted"]
            ).grid(row=0, column=col, padx=4, pady=(10, 4), sticky="nsew")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=16, pady=(0, 14))

        ctk.CTkButton(
            footer, text="Confirmar Fecha", fg_color=PALETTE["mint"], hover_color=PALETTE["mint_hover"],
            font=("Segoe UI", 13, "bold"), height=38, command=self._confirmar
        ).pack(fill="x")

    def _dibujar_mes(self):
        if self.anio_actual == self.hoy.year and self.mes_actual <= self.hoy.month:
            self.btn_prev.configure(state="disabled")
        else:
            self.btn_prev.configure(state="normal")

        nombre_mes = calendar.month_name[self.mes_actual].capitalize()
        self.lbl_mes_anio.configure(text=f"{nombre_mes} {self.anio_actual}")

        for w in self.grid_frame.winfo_children():
            info = w.grid_info()
            if int(info.get("row", 0)) > 0:
                w.destroy()

        cal = calendar.monthcalendar(self.anio_actual, self.mes_actual)
        for r, semana in enumerate(cal, start=1):
            for c, dia_num in enumerate(semana):
                if dia_num == 0:
                    continue

                dia_fecha = date(self.anio_actual, self.mes_actual, dia_num)
                es_pasado = dia_fecha < self.hoy
                es_hoy = dia_fecha == self.hoy
                es_seleccionado = dia_fecha == self.fecha_seleccionada

                if es_pasado:
                    color_btn = "#E2E8F0"
                    color_texto = "#94A3B8"
                    estado = "disabled"
                elif es_seleccionado:
                    color_btn = PALETTE["accent"]
                    color_texto = "#FFFFFF"
                    estado = "normal"
                elif es_hoy:
                    color_btn = PALETTE["mint"]
                    color_texto = "#FFFFFF"
                    estado = "normal"
                else:
                    color_btn = "#F1F5F9"
                    color_texto = PALETTE["text_dark"]
                    estado = "normal"

                btn = ctk.CTkButton(
                    self.grid_frame, text=str(dia_num), width=36, height=34,
                    corner_radius=8, fg_color=color_btn, text_color=color_texto,
                    hover_color=PALETTE["sidebar_hover"] if not es_pasado else "#E2E8F0",
                    font=("Segoe UI", 11, "bold"), state=estado,
                    command=lambda f=dia_fecha: self._seleccionar(f)
                )
                btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")

        for c in range(7):
            self.grid_frame.grid_columnconfigure(c, weight=1)

    def _seleccionar(self, f: date):
        self.fecha_seleccionada = f
        self._dibujar_mes()

    def _mes_anterior(self):
        if self.mes_actual == 1:
            self.mes_actual = 12
            self.anio_actual -= 1
        else:
            self.mes_actual -= 1
        self._dibujar_mes()

    def _mes_siguiente(self):
        if self.mes_actual == 12:
            self.mes_actual = 1
            self.anio_actual += 1
        else:
            self.mes_actual += 1
        self._dibujar_mes()

    def _confirmar(self):
        self.on_date_selected(self.fecha_seleccionada.isoformat())
        self.destroy()


# =========================================================================
# MODAL DE RELOJ DIGITAL Y CUADRANTE DE CONSULTA
# =========================================================================
class VetClockModal(ctk.CTkToplevel):
    def __init__(self, parent, hora_inicial: str, fecha_cita: str, on_time_selected):
        super().__init__(parent)
        self.title("Horario de Consulta")
        self.geometry("360x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_time_selected = on_time_selected
        self.fecha_cita = fecha_cita
        self.hora = 10
        self.minuto = 0

        try:
            partes = hora_inicial.split(":")
            self.hora = int(partes[0])
            self.minuto = int(partes[1])
        except Exception:
            pass

        self.configure(fg_color=PALETTE["bg_main"])
        self._construir_ui()

    def _construir_ui(self):
        card = ctk.CTkFrame(self, fg_color=PALETTE["card"], corner_radius=14)
        card.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            card, text="🕒 RELOJ DE CONSULTA", font=("Segoe UI", 15, "bold"),
            text_color=PALETTE["primary"]
        ).pack(pady=(16, 8))

        clock_display = ctk.CTkFrame(card, fg_color=PALETTE["sidebar"], corner_radius=12, height=75)
        clock_display.pack(fill="x", padx=25, pady=8)
        clock_display.pack_propagate(False)

        self.lbl_reloj = ctk.CTkLabel(
            clock_display, text="", font=("Segoe UI", 34, "bold"), text_color="#A7F3D0"
        )
        self.lbl_reloj.place(relx=0.5, rely=0.5, anchor="center")

        controls = ctk.CTkFrame(card, fg_color="transparent")
        controls.pack(fill="x", padx=25, pady=10)

        # Ajuste de Horas
        h_box = ctk.CTkFrame(controls, fg_color="#F8FAFC", corner_radius=8)
        h_box.pack(side="left", expand=True, fill="both", padx=4, pady=4)
        ctk.CTkLabel(h_box, text="Hora (08 - 20)", font=("Segoe UI", 11, "bold"), text_color=PALETTE["text_muted"]).pack(pady=4)
        ctk.CTkButton(h_box, text="▲ +1h", width=75, height=28, fg_color=PALETTE["primary"], command=lambda: self._ajustar_hora(1)).pack(pady=2)
        ctk.CTkButton(h_box, text="▼ -1h", width=75, height=28, fg_color=PALETTE["primary"], command=lambda: self._ajustar_hora(-1)).pack(pady=4)

        # Ajuste de Minutos
        m_box = ctk.CTkFrame(controls, fg_color="#F8FAFC", corner_radius=8)
        m_box.pack(side="right", expand=True, fill="both", padx=4, pady=4)
        ctk.CTkLabel(m_box, text="Minuto (:00 :15 :30 :45)", font=("Segoe UI", 11, "bold"), text_color=PALETTE["text_muted"]).pack(pady=4)
        ctk.CTkButton(m_box, text="▲ +15m", width=75, height=28, fg_color=PALETTE["accent"], command=lambda: self._ajustar_minuto(15)).pack(pady=2)
        ctk.CTkButton(m_box, text="▼ -15m", width=75, height=28, fg_color=PALETTE["accent"], command=lambda: self._ajustar_minuto(-15)).pack(pady=4)

        # Atajos Rápidos
        ctk.CTkLabel(card, text="Turnos Frecuentes:", font=("Segoe UI", 11, "bold"), text_color=PALETTE["text_muted"]).pack(pady=(6, 2))
        quick_frame = ctk.CTkFrame(card, fg_color="transparent")
        quick_frame.pack(pady=2)

        for h_str in ["09:00", "11:30", "14:00", "17:00"]:
            ctk.CTkButton(
                quick_frame, text=h_str, width=62, height=26, corner_radius=6,
                fg_color="#E0F2F1", text_color=PALETTE["primary"], hover_color=PALETTE["sidebar_hover"],
                font=("Segoe UI", 10, "bold"), command=lambda val=h_str: self._set_quick_time(val)
            ).pack(side="left", padx=3)

        ctk.CTkButton(
            card, text="Confirmar Horario", fg_color=PALETTE["mint"], hover_color=PALETTE["mint_hover"],
            font=("Segoe UI", 13, "bold"), height=38, command=self._confirmar
        ).pack(fill="x", padx=25, pady=(15, 12))

        self._actualizar_display()

    def _ajustar_hora(self, delta: int):
        self.hora = max(8, min(20, self.hora + delta))
        self._actualizar_display()

    def _ajustar_minuto(self, delta: int):
        nuevos_minutos = self.minuto + delta
        if nuevos_minutos >= 60:
            self.minuto = 0
            self._ajustar_hora(1)
        elif nuevos_minutos < 0:
            self.minuto = 45
            self._ajustar_hora(-1)
        else:
            self.minuto = nuevos_minutos
        self._actualizar_display()

    def _set_quick_time(self, h_str: str):
        hh, mm = h_str.split(":")
        self.hora = int(hh)
        self.minuto = int(mm)
        self._actualizar_display()

    def _actualizar_display(self):
        self.lbl_reloj.configure(text=f"{self.hora:02d}:{self.minuto:02d}")

    def _confirmar(self):
        if self.fecha_cita == date.today().isoformat():
            ahora = datetime.now()
            if time(self.hora, self.minuto) <= ahora.time():
                messagebox.showwarning(
                    "Horario Inválido",
                    f"No puedes seleccionar una hora anterior a la actual ({ahora.strftime('%H:%M')}) para citas de hoy."
                )
                return

        self.on_time_selected(f"{self.hora:02d}:{self.minuto:02d}")
        self.destroy()


# =========================================================================
# APLICACIÓN PRINCIPAL PETCARE
# =========================================================================
class PetCareApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🐾 PetCare Enterprise - Sistema de Gestión Clínica Veterinaria")
        self.geometry("1280x780")
        self.minsize(1120, 700)
        self.configure(fg_color=PALETTE["bg_main"])

        self.db = DatabaseManager()
        self.repo = PetCareRepository(self.db)
        self.sound = SoundManager()
        self.current_user = None

        self._configure_treeview_style()

        self.root_container = ctk.CTkFrame(self, fg_color=PALETTE["bg_main"], corner_radius=0)
        self.root_container.pack(fill="both", expand=True)

        self.attributes("-alpha", 0.0)
        self._animate_window_fade_in(0.0)

        self.mostrar_login()

    def _animate_window_fade_in(self, alpha: float):
        if alpha < 1.0:
            alpha = min(1.0, alpha + 0.08)
            self.attributes("-alpha", alpha)
            self.after(16, lambda: self._animate_window_fade_in(alpha))

    def _animate_slide_in(self, widget: ctk.CTkFrame, start_x: float = 0.06, step: float = 0.012):
        if start_x > 0.0:
            next_x = max(0.0, start_x - step)
            widget.place(relx=next_x, rely=0.0, relwidth=1.0, relheight=1.0)
            self.after(10, lambda: self._animate_slide_in(widget, next_x, step))
        else:
            widget.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

    def _configure_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Vet.Treeview",
            background="#FFFFFF",
            foreground=PALETTE["text_dark"],
            rowheight=30,
            fieldbackground="#FFFFFF",
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.configure(
            "Vet.Treeview.Heading",
            background=PALETTE["primary"],
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
        )
        style.map(
            "Vet.Treeview",
            background=[("selected", PALETTE["accent"])],
            foreground=[("selected", "#FFFFFF")],
        )

    # --- VISTA LOGIN (RF-06) ---
    def mostrar_login(self):
        for w in self.root_container.winfo_children():
            w.destroy()

        bg_frame = ctk.CTkFrame(self.root_container, fg_color=PALETTE["sidebar"], corner_radius=0)
        bg_frame.pack(fill="both", expand=True)

        card = ctk.CTkFrame(bg_frame, width=420, height=470, fg_color=PALETTE["card"], corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text="🐾 PETCARE CLINIC", font=("Segoe UI", 26, "bold"), text_color=PALETTE["primary"]
        ).pack(pady=(35, 5))
        ctk.CTkLabel(
            card, text="Acceso al Sistema de Gestión Veterinaria", font=("Segoe UI", 13), text_color=PALETTE["text_muted"]
        ).pack(pady=(0, 25))

        self.user_entry = ctk.CTkEntry(
            card, placeholder_text="Usuario (admin o recepcion)", width=300, height=42, corner_radius=10
        )
        self.user_entry.pack(pady=10)
        self.user_entry.insert(0, "admin")

        self.pass_entry = ctk.CTkEntry(
            card, placeholder_text="Contraseña", show="*", width=300, height=42, corner_radius=10
        )
        self.pass_entry.pack(pady=10)
        self.pass_entry.insert(0, "admin123")

        ctk.CTkButton(
            card,
            text="INGRESAR AL SISTEMA",
            width=300,
            height=45,
            corner_radius=10,
            fg_color=PALETTE["accent"],
            hover_color=PALETTE["accent_hover"],
            font=("Segoe UI", 14, "bold"),
            command=self._procesar_login,
        ).pack(pady=25)

        ctk.CTkLabel(
            card,
            text="Cuentas demo:\nAdmin: admin / admin123 (Control Total)\nRecepción: recepcion / vet123 (Sin borrado)",
            font=("Segoe UI", 11),
            text_color=PALETTE["text_muted"],
        ).pack(pady=5)

    def _procesar_login(self):
        user = self.repo.autenticar(self.user_entry.get().strip(), self.pass_entry.get().strip())
        if user:
            self.current_user = user
            self.sound.play_cat_meow()
            self.mostrar_layout_principal()
        else:
            messagebox.showerror("Acceso Denegado", "Credenciales incorrectas.")

    # --- SHELL PRINCIPAL ---
    def mostrar_layout_principal(self):
        for w in self.root_container.winfo_children():
            w.destroy()

        self.sidebar = ctk.CTkFrame(self.root_container, width=250, fg_color=PALETTE["sidebar"], corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="🐾 PETCARE\nVETERINARIA", font=("Segoe UI", 22, "bold"), text_color="#FFFFFF"
        ).pack(pady=(25, 10))

        rol_badge = "ADMINISTRADOR" if self.current_user["rol"] == "admin" else "RECEPCIONISTA"
        ctk.CTkLabel(
            self.sidebar,
            text=f"👤 {self.current_user['username'].upper()} [{rol_badge}]",
            font=("Segoe UI", 11, "bold"),
            text_color="#A7F3D0",
        ).pack(pady=(0, 20))

        nav_items = [
            ("📊 Panel y Buscador (RF-04)", self.vista_dashboard),
            ("👥 Clientes (RF-02/08/09)", self.vista_clientes),
            ("🐶 Mascotas (RF-03/08/09)", self.vista_mascotas),
            ("📅 Agendar Cita + PDF (RF-01/10)", self.vista_citas),
            ("📆 Citas del Día (RF-07)", self.vista_citas_dia),
            ("📋 Historial Clínico (RF-05)", self.vista_historial),
        ]

        for texto, comando in nav_items:
            ctk.CTkButton(
                self.sidebar,
                text=texto,
                anchor="w",
                width=220,
                height=42,
                corner_radius=10,
                fg_color="transparent",
                hover_color=PALETTE["sidebar_hover"],
                font=("Segoe UI", 13, "bold"),
                command=lambda cmd=comando: self._cambiar_vista(cmd),
            ).pack(pady=4, padx=15)

        self.sound_switch = ctk.CTkSwitch(
            self.sidebar,
            text="Sonidos Minecraft 🐺🐱",
            text_color="#FFFFFF",
            progress_color=PALETTE["accent"],
            command=self._toggle_sound,
        )
        self.sound_switch.select()
        self.sound_switch.pack(side="bottom", pady=15, padx=20)

        ctk.CTkButton(
            self.sidebar,
            text="Cerrar Sesión",
            fg_color=PALETTE["danger"],
            hover_color="#DC2626",
            width=200,
            command=self.mostrar_login,
        ).pack(side="bottom", pady=10)

        self.main_area = ctk.CTkFrame(self.root_container, fg_color=PALETTE["bg_main"], corner_radius=0)
        self.main_area.pack(side="right", fill="both", expand=True)

        self._cambiar_vista(self.vista_dashboard)

    def _toggle_sound(self):
        self.sound.enabled = bool(self.sound_switch.get())

    def _cambiar_vista(self, builder_func):
        for w in self.main_area.winfo_children():
            w.destroy()
        view_frame = ctk.CTkFrame(self.main_area, fg_color=PALETTE["bg_main"], corner_radius=0)
        builder_func(view_frame)
        self._animate_slide_in(view_frame)

    def _es_admin(self) -> bool:
        return self.current_user and self.current_user.get("rol") == "admin"

    # --- VISTA 1: DASHBOARD Y BÚSQUEDA GLOBAL (RF-04) ---
    def vista_dashboard(self, parent: ctk.CTkFrame):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))
        ctk.CTkLabel(
            header, text="Panel de Control y Búsqueda Inteligente", font=("Segoe UI", 24, "bold"), text_color=PALETTE["primary"]
        ).pack(side="left")

        kpi_frame = ctk.CTkFrame(parent, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=20, pady=10)

        total_clientes = len(self.repo.listar_clientes())
        total_mascotas = len(self.repo.listar_mascotas())
        citas_hoy = len(self.repo.buscar_citas(fecha_exacta=date.today().isoformat()))

        kpis = [
            ("CLIENTES REGISTRADOS", str(total_clientes), PALETTE["primary"]),
            ("PACIENTES (MASCOTAS)", str(total_mascotas), PALETTE["mint"]),
            (f"CITAS PARA HOY ({date.today().isoformat()})", str(citas_hoy), PALETTE["accent"]),
        ]
        for titulo, valor, color in kpis:
            card = ctk.CTkFrame(kpi_frame, fg_color=PALETTE["card"], corner_radius=14, height=105)
            card.pack(side="left", fill="x", expand=True, padx=8)
            ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 12, "bold"), text_color=PALETTE["text_muted"]).pack(
                anchor="w", padx=18, pady=(15, 2)
            )
            ctk.CTkLabel(card, text=valor, font=("Segoe UI", 30, "bold"), text_color=color).pack(
                anchor="w", padx=18, pady=(0, 12)
            )

        search_card = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        search_card.pack(fill="both", expand=True, padx=25, pady=15)

        bar = ctk.CTkFrame(search_card, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(bar, text="🔍 Filtro Rápido (Dueño, Mascota o Fecha):", font=("Segoe UI", 14, "bold")).pack(
            side="left", padx=(0, 10)
        )
        entry_filtro = ctk.CTkEntry(bar, placeholder_text="Ej. Firulais, Juan, 2026-10-24...", width=340)
        entry_filtro.pack(side="left", padx=5)

        cols = ("ID", "Fecha", "Hora", "Mascota", "Especie", "Dueño", "Teléfono", "Motivo", "Estado")
        tree = ttk.Treeview(search_card, columns=cols, show="headings", style="Vet.Treeview")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=105 if c != "Motivo" else 180, anchor="center")
        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        def ejecutar_busqueda(*_):
            for item in tree.get_children():
                tree.delete(item)
            for r in self.repo.buscar_citas(filtro_texto=entry_filtro.get()):
                tree.insert(
                    "",
                    "end",
                    values=(
                        r["id"], r["fecha"], r["hora"], r["mascota_nombre"],
                        r["especie"], r["dueno_nombre"], r["dueno_telefono"], r["motivo"], r["estado"]
                    ),
                )

        ctk.CTkButton(bar, text="Buscar", fg_color=PALETTE["primary"], width=110, command=ejecutar_busqueda).pack(
            side="left", padx=6
        )
        entry_filtro.bind("<KeyRelease>", ejecutar_busqueda)
        ejecutar_busqueda()

    # --- VISTA 2: CLIENTES (RF-02, RF-08, RF-09) ---
    def vista_clientes(self, parent: ctk.CTkFrame):
        selected_id = {"id": None}

        ctk.CTkLabel(
            parent, text="Gestión de Clientes (Propietarios)", font=("Segoe UI", 24, "bold"), text_color=PALETTE["primary"]
        ).pack(anchor="w", padx=25, pady=(20, 10))

        form = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        form.pack(fill="x", padx=25, pady=8)

        e_nombre = ctk.CTkEntry(form, placeholder_text="Nombre completo del cliente", width=260)
        e_domicilio = ctk.CTkEntry(form, placeholder_text="Domicilio completo", width=300)
        e_telefono = ctk.CTkEntry(form, placeholder_text="Teléfono (10 dígitos)", width=180)

        e_nombre.grid(row=0, column=0, padx=12, pady=15)
        e_domicilio.grid(row=0, column=1, padx=12, pady=15)
        e_telefono.grid(row=0, column=2, padx=12, pady=15)

        table_frame = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        table_frame.pack(fill="both", expand=True, padx=25, pady=10)

        cols = ("ID", "Nombre", "Domicilio", "Teléfono", "Fecha Registro")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="Vet.Treeview")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=180 if c != "ID" else 60, anchor="center")
        tree.pack(fill="both", expand=True, padx=15, pady=15)

        def recargar():
            for i in tree.get_children():
                tree.delete(i)
            for c in self.repo.listar_clientes():
                tree.insert("", "end", values=(c["id"], c["nombre"], c["domicilio"], c["telefono"], c["fecha_registro"]))

        def limpiar():
            selected_id["id"] = None
            e_nombre.delete(0, "end")
            e_domicilio.delete(0, "end")
            e_telefono.delete(0, "end")

        def guardar():
            if not e_nombre.get().strip() or not e_telefono.get().strip():
                messagebox.showwarning("Validación", "Nombre y teléfono son obligatorios.")
                return
            if selected_id["id"] is None:
                self.repo.crear_cliente(e_nombre.get(), e_domicilio.get(), e_telefono.get())
            else:
                self.repo.actualizar_cliente(selected_id["id"], e_nombre.get(), e_domicilio.get(), e_telefono.get())
            self.sound.play_wolf_bark()
            limpiar()
            recargar()

        def eliminar():
            if not self._es_admin():
                messagebox.showerror("RF-06 Permisos", "Solo los administradores pueden eliminar registros.")
                return
            if selected_id["id"] and messagebox.askyesno("Confirmar", "¿Eliminar cliente y sus mascotas asociadas?"):
                self.repo.eliminar_cliente(selected_id["id"])
                self.sound.play_cat_meow()
                limpiar()
                recargar()

        def seleccionar(_event):
            sel = tree.selection()
            if sel:
                vals = tree.item(sel[0], "values")
                selected_id["id"] = int(vals[0])
                e_nombre.delete(0, "end")
                e_nombre.insert(0, vals[1])
                e_domicilio.delete(0, "end")
                e_domicilio.insert(0, vals[2])
                e_telefono.delete(0, "end")
                e_telefono.insert(0, vals[3])

        tree.bind("<<TreeviewSelect>>", seleccionar)

        ctk.CTkButton(form, text="Guardar (OK)", fg_color=PALETTE["mint"], hover_color=PALETTE["mint_hover"], command=guardar).grid(
            row=0, column=3, padx=8
        )
        ctk.CTkButton(form, text="Limpiar", fg_color=PALETTE["text_muted"], width=90, command=limpiar).grid(
            row=0, column=4, padx=5
        )
        btn_del = ctk.CTkButton(
            form,
            text="Eliminar",
            fg_color=PALETTE["danger"] if self._es_admin() else "#94A3B8",
            state="normal" if self._es_admin() else "disabled",
            command=eliminar,
        )
        btn_del.grid(row=0, column=5, padx=8)

        recargar()

    # --- VISTA 3: MASCOTAS (RF-03, RF-08, RF-09) ---
    def vista_mascotas(self, parent: ctk.CTkFrame):
        selected_id = {"id": None}
        clientes = self.repo.listar_clientes()
        mapa_clientes = {f"{c['id']} - {c['nombre']}": c["id"] for c in clientes}

        ctk.CTkLabel(
            parent, text="Registro Clínico de Mascotas", font=("Segoe UI", 24, "bold"), text_color=PALETTE["primary"]
        ).pack(anchor="w", padx=25, pady=(20, 10))

        form = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        form.pack(fill="x", padx=25, pady=8)

        cb_cliente = ctk.CTkComboBox(
            form, values=list(mapa_clientes.keys()) if mapa_clientes else ["Sin clientes"], width=230
        )
        e_nombre = ctk.CTkEntry(form, placeholder_text="Nombre Mascota", width=160)
        cb_especie = ctk.CTkComboBox(form, values=["Perro", "Gato", "Ave", "Exótico"], width=120)
        e_raza = ctk.CTkEntry(form, placeholder_text="Raza", width=150)
        e_edad = ctk.CTkEntry(form, placeholder_text="Edad", width=120)
        e_alergias = ctk.CTkEntry(form, placeholder_text="Alergias", width=200)
        e_vacunas = ctk.CTkEntry(form, placeholder_text="Vacunas", width=200)

        cb_cliente.grid(row=0, column=0, padx=8, pady=10)
        e_nombre.grid(row=0, column=1, padx=8, pady=10)
        cb_especie.grid(row=0, column=2, padx=8, pady=10)
        e_raza.grid(row=0, column=3, padx=8, pady=10)
        e_edad.grid(row=0, column=4, padx=8, pady=10)
        e_alergias.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8, pady=10)
        e_vacunas.grid(row=1, column=2, columnspan=2, sticky="ew", padx=8, pady=10)

        table_frame = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        table_frame.pack(fill="both", expand=True, padx=25, pady=10)

        cols = ("ID", "Mascota", "Especie", "Raza", "Edad", "Alergias", "Vacunas", "ID Dueño", "Dueño")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="Vet.Treeview")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=115 if c != "ID" else 55, anchor="center")
        tree.pack(fill="both", expand=True, padx=15, pady=15)

        def recargar():
            for i in tree.get_children():
                tree.delete(i)
            for m in self.repo.listar_mascotas():
                tree.insert(
                    "",
                    "end",
                    values=(
                        m["id"], m["nombre"], m["especie"], m["raza"], m["edad"],
                        m["alergias"], m["vacunas"], m["cliente_id"], m["dueno_nombre"]
                    ),
                )

        def guardar():
            if not mapa_clientes:
                messagebox.showwarning("Atención", "Primero registra al menos un cliente.")
                return
            cliente_id = mapa_clientes.get(cb_cliente.get())
            if not cliente_id or not e_nombre.get().strip():
                messagebox.showwarning("Validación", "Selecciona un dueño e ingresa el nombre de la mascota.")
                return

            alergias = e_alergias.get().strip() or "Ninguna"
            vacunas = e_vacunas.get().strip() or "Al día"

            if selected_id["id"] is None:
                self.repo.crear_mascota(
                    cliente_id, e_nombre.get(), cb_especie.get(), e_raza.get(), e_edad.get(), alergias, vacunas
                )
            else:
                self.repo.actualizar_mascota(
                    selected_id["id"], cliente_id, e_nombre.get(), cb_especie.get(), e_raza.get(), e_edad.get(), alergias, vacunas
                )

            if cb_especie.get() == "Gato":
                self.sound.play_cat_meow()
            else:
                self.sound.play_wolf_bark()

            selected_id["id"] = None
            e_nombre.delete(0, "end")
            e_raza.delete(0, "end")
            e_edad.delete(0, "end")
            e_alergias.delete(0, "end")
            e_vacunas.delete(0, "end")
            recargar()

        def eliminar():
            if not self._es_admin():
                return
            if selected_id["id"] and messagebox.askyesno("Confirmar", "¿Eliminar mascota y sus registros?"):
                self.repo.eliminar_mascota(selected_id["id"])
                self.sound.play_wolf_bark()
                selected_id["id"] = None
                recargar()

        def seleccionar(_e):
            sel = tree.selection()
            if sel:
                v = tree.item(sel[0], "values")
                selected_id["id"] = int(v[0])
                e_nombre.delete(0, "end")
                e_nombre.insert(0, v[1])
                cb_especie.set(v[2])
                e_raza.delete(0, "end")
                e_raza.insert(0, v[3])
                e_edad.delete(0, "end")
                e_edad.insert(0, v[4])
                e_alergias.delete(0, "end")
                e_alergias.insert(0, v[5])
                e_vacunas.delete(0, "end")
                e_vacunas.insert(0, v[6])
                cb_cliente.set(f"{v[7]} - {v[8]}")

        tree.bind("<<TreeviewSelect>>", seleccionar)

        ctk.CTkButton(form, text="Guardar Mascota (OK)", fg_color=PALETTE["mint"], command=guardar).grid(
            row=1, column=4, padx=8
        )
        ctk.CTkButton(
            form,
            text="Eliminar",
            fg_color=PALETTE["danger"] if self._es_admin() else "#94A3B8",
            state="normal" if self._es_admin() else "disabled",
            command=eliminar,
        ).grid(row=1, column=5, padx=8)

        recargar()

    # --- VISTA 4: AGENDAR CITAS (CASCADA DUEÑO -> MASCOTA) + MODALES + PDF ---
    def vista_citas(self, parent: ctk.CTkFrame):
        selected_cita = {"id": None}
        todos_clientes = self.repo.listar_clientes()
        mapa_clientes = {f"{c['id']} - {c['nombre']}": c["id"] for c in todos_clientes}
        mapa_mascotas_actuales = {}

        ctk.CTkLabel(
            parent,
            text="Agenda de Citas y Emisión de Comprobantes PDF",
            font=("Segoe UI", 24, "bold"),
            text_color=PALETTE["primary"],
        ).pack(anchor="w", padx=25, pady=(20, 10))

        form = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        form.pack(fill="x", padx=25, pady=8)

        # 1. Dueño
        ctk.CTkLabel(form, text="1. Dueño:", font=("Segoe UI", 12, "bold"), text_color=PALETTE["text_dark"]).grid(
            row=0, column=0, padx=(15, 5), pady=(12, 2), sticky="w"
        )
        cb_dueno = ctk.CTkComboBox(
            form,
            values=list(mapa_clientes.keys()) if mapa_clientes else ["Sin clientes registrados"],
            width=260,
        )
        cb_dueno.grid(row=1, column=0, padx=(15, 10), pady=(0, 10), sticky="w")

        # 2. Mascota (en cascada)
        ctk.CTkLabel(form, text="2. Mascota:", font=("Segoe UI", 12, "bold"), text_color=PALETTE["text_dark"]).grid(
            row=0, column=1, padx=5, pady=(12, 2), sticky="w"
        )
        cb_mascota = ctk.CTkComboBox(
            form,
            values=["Selecciona un dueño"],
            width=220,
            state="disabled"
        )
        cb_mascota.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="w")

        # 3. Fecha (Modal Calendario)
        ctk.CTkLabel(form, text="Fecha:", font=("Segoe UI", 12, "bold"), text_color=PALETTE["text_dark"]).grid(
            row=0, column=2, padx=5, pady=(12, 2), sticky="w"
        )
        self.btn_fecha_picker = ctk.CTkButton(
            form,
            text=f"📅 {date.today().isoformat()}",
            width=145,
            height=34,
            corner_radius=8,
            fg_color="#E0F2F1",
            text_color=PALETTE["primary"],
            hover_color="#B2DFDB",
            font=("Segoe UI", 12, "bold"),
            command=lambda: VetCalendarModal(
                self,
                self.btn_fecha_picker.cget("text").replace("📅 ", "").strip(),
                lambda d: self.btn_fecha_picker.configure(text=f"📅 {d}")
            )
        )
        self.btn_fecha_picker.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="w")

        # 4. Horario (Modal Reloj)
        ctk.CTkLabel(form, text="Horario:", font=("Segoe UI", 12, "bold"), text_color=PALETTE["text_dark"]).grid(
            row=0, column=3, padx=5, pady=(12, 2), sticky="w"
        )
        self.btn_hora_picker = ctk.CTkButton(
            form,
            text="🕒 10:00",
            width=115,
            height=34,
            corner_radius=8,
            fg_color="#FEF3C7",
            text_color="#92400E",
            hover_color="#FDE68A",
            font=("Segoe UI", 12, "bold"),
            command=lambda: VetClockModal(
                self,
                self.btn_hora_picker.cget("text").replace("🕒 ", "").strip(),
                self.btn_fecha_picker.cget("text").replace("📅 ", "").strip(),
                lambda h: self.btn_hora_picker.configure(text=f"🕒 {h}")
            )
        )
        self.btn_hora_picker.grid(row=1, column=3, padx=5, pady=(0, 10), sticky="w")

        # 5. Estado
        ctk.CTkLabel(form, text="Estado:", font=("Segoe UI", 12, "bold"), text_color=PALETTE["text_dark"]).grid(
            row=0, column=4, padx=5, pady=(12, 2), sticky="w"
        )
        cb_estado = ctk.CTkComboBox(form, values=["Programada", "Atendida", "Cancelada"], width=130)
        cb_estado.grid(row=1, column=4, padx=(5, 15), pady=(0, 10), sticky="w")

        # Fila 2: Motivo y Notas
        ctk.CTkLabel(form, text="Motivo del Servicio:", font=("Segoe UI", 12, "bold"), text_color=PALETTE["text_dark"]).grid(
            row=2, column=0, padx=(15, 5), pady=(5, 2), sticky="w"
        )
        e_motivo = ctk.CTkEntry(form, placeholder_text="Ej. Consulta general, Vacunación...", width=260)
        e_motivo.grid(row=3, column=0, padx=(15, 10), pady=(0, 15), sticky="w")

        ctk.CTkLabel(form, text="Notas Clínicas / Tratamiento:", font=("Segoe UI", 12, "bold"), text_color=PALETTE["text_dark"]).grid(
            row=2, column=1, columnspan=2, padx=5, pady=(5, 2), sticky="w"
        )
        e_notas = ctk.CTkEntry(form, placeholder_text="Diagnóstico, medicamentos o indicaciones...", width=365)
        e_notas.grid(row=3, column=1, columnspan=2, padx=5, pady=(0, 15), sticky="w")

        btn_box = ctk.CTkFrame(form, fg_color="transparent")
        btn_box.grid(row=3, column=3, columnspan=2, padx=(5, 15), pady=(0, 15), sticky="e")

        table_frame = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        table_frame.pack(fill="both", expand=True, padx=25, pady=10)

        cols = ("ID", "Fecha", "Hora", "Mascota", "Dueño", "Motivo", "Estado")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="Vet.Treeview")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=130 if c != "ID" else 55, anchor="center")
        tree.pack(fill="both", expand=True, padx=15, pady=15)

        def on_dueno_cambiado(eleccion):
            cliente_id = mapa_clientes.get(eleccion)
            mapa_mascotas_actuales.clear()
            if cliente_id:
                todas_m = self.repo.listar_mascotas()
                mascotas_dueno = [m for m in todas_m if m["cliente_id"] == cliente_id]
                if mascotas_dueno:
                    for m in mascotas_dueno:
                        mapa_mascotas_actuales[f"{m['id']} - {m['nombre']} ({m['especie']})"] = m["id"]
                    lista_nombres = list(mapa_mascotas_actuales.keys())
                    cb_mascota.configure(state="normal", values=lista_nombres)
                    cb_mascota.set(lista_nombres[0])
                else:
                    cb_mascota.configure(state="normal", values=["Sin mascotas registradas"])
                    cb_mascota.set("Sin mascotas registradas")
            else:
                cb_mascota.configure(state="disabled", values=["Selecciona un dueño"])
                cb_mascota.set("Selecciona un dueño")

        cb_dueno.configure(command=on_dueno_cambiado)

        def recargar():
            for i in tree.get_children():
                tree.delete(i)
            for ci in self.repo.buscar_citas():
                tree.insert(
                    "",
                    "end",
                    values=(
                        ci["id"], ci["fecha"], ci["hora"], ci["mascota_nombre"],
                        ci["dueno_nombre"], ci["motivo"], ci["estado"]
                    ),
                )

        def limpiar():
            selected_cita["id"] = None
            e_motivo.delete(0, "end")
            e_notas.delete(0, "end")
            cb_estado.set("Programada")

        def guardar_cita():
            mascota_id = mapa_mascotas_actuales.get(cb_mascota.get())
            if not mascota_id:
                messagebox.showwarning("Validación", "Debes seleccionar un dueño y una mascota válida.")
                return

            fecha_val = self.btn_fecha_picker.cget("text").replace("📅 ", "").strip()
            hora_val = self.btn_hora_picker.cget("text").replace("🕒 ", "").strip()
            motivo = e_motivo.get().strip() or "Consulta General"

            if selected_cita["id"] is None:
                cita_id = self.repo.agendar_cita(mascota_id, fecha_val, hora_val, motivo)
                msg = f"Cita #{cita_id} registrada con éxito."
            else:
                cita_id = selected_cita["id"]
                self.repo.actualizar_cita(
                    cita_id, fecha_val, hora_val, motivo, cb_estado.get(), e_notas.get()
                )
                msg = f"Cita #{cita_id} actualizada correctamente."

            self.sound.play_wolf_bark()
            limpiar()
            recargar()
            messagebox.showinfo("PetCare", msg)

        def descargar_pdf_manual():
            cita_id = selected_cita["id"]
            if not cita_id:
                sel = tree.selection()
                if sel:
                    cita_id = int(tree.item(sel[0], "values")[0])

            if not cita_id:
                messagebox.showinfo(
                    "Descargar PDF",
                    "Por favor selecciona una cita de la tabla para generar y descargar su comprobante PDF."
                )
                return

            detalle = self.repo.obtener_detalle_cita(cita_id)
            if detalle:
                ruta_pdf = PDFReceiptGenerator.generar_comprobante_cita(detalle)
                self.sound.play_cat_meow()
                messagebox.showinfo(
                    "Comprobante Generado",
                    f"El PDF de la cita #{cita_id} se ha generado en:\n{ruta_pdf}"
                )

        def cancelar_cita():
            if not selected_cita["id"]:
                messagebox.showinfo("Selección", "Selecciona una cita de la tabla para cancelarla.")
                return
            fecha_val = self.btn_fecha_picker.cget("text").replace("📅 ", "").strip()
            hora_val = self.btn_hora_picker.cget("text").replace("🕒 ", "").strip()
            self.repo.actualizar_cita(
                selected_cita["id"], fecha_val, hora_val, e_motivo.get(), "Cancelada", e_notas.get()
            )
            self.sound.play_cat_meow()
            limpiar()
            recargar()

        def seleccionar_fila(_e):
            sel = tree.selection()
            if sel:
                cid = int(tree.item(sel[0], "values")[0])
                det = self.repo.obtener_detalle_cita(cid)
                if det:
                    selected_cita["id"] = cid
                    texto_dueno = f"{det['cliente_id']} - {det['dueno_nombre']}"
                    cb_dueno.set(texto_dueno)
                    on_dueno_cambiado(texto_dueno)

                    texto_mascota = f"{det['mascota_id']} - {det['mascota_nombre']} ({det['especie']})"
                    cb_mascota.set(texto_mascota)

                    self.btn_fecha_picker.configure(text=f"📅 {det['fecha']}")
                    self.btn_hora_picker.configure(text=f"🕒 {det['hora']}")
                    e_motivo.delete(0, "end")
                    e_motivo.insert(0, det["motivo"])
                    cb_estado.set(det["estado"])
                    e_notas.delete(0, "end")
                    e_notas.insert(0, det.get("notas_clinicas") or "")

        tree.bind("<<TreeviewSelect>>", seleccionar_fila)

        ctk.CTkButton(
            btn_box,
            text="Confirmar Cita (OK)",
            fg_color=PALETTE["mint"],
            hover_color=PALETTE["mint_hover"],
            font=("Segoe UI", 12, "bold"),
            width=140,
            command=guardar_cita,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_box,
            text="📄 Descargar PDF",
            fg_color=PALETTE["accent"],
            hover_color=PALETTE["accent_hover"],
            font=("Segoe UI", 12, "bold"),
            width=130,
            command=descargar_pdf_manual,
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_box,
            text="Cancelar Cita",
            fg_color=PALETTE["danger"],
            width=100,
            command=cancelar_cita,
        ).pack(side="left", padx=4)

        if mapa_clientes:
            primer_dueno = list(mapa_clientes.keys())[0]
            cb_dueno.set(primer_dueno)
            on_dueno_cambiado(primer_dueno)

        recargar()

    # --- VISTA 5: CITAS PROGRAMADAS POR FECHA ESPECÍFICA (RF-07) ---
    def vista_citas_dia(self, parent: ctk.CTkFrame):
        ctk.CTkLabel(
            parent, text="Agenda de Citas por Fecha Específica (RF-07)", font=("Segoe UI", 24, "bold"), text_color=PALETTE["primary"]
        ).pack(anchor="w", padx=25, pady=(20, 10))

        top_bar = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        top_bar.pack(fill="x", padx=25, pady=8)

        ctk.CTkLabel(top_bar, text="Fecha a consultar:", font=("Segoe UI", 13, "bold")).pack(
            side="left", padx=15, pady=15
        )

        btn_filtro_fecha = ctk.CTkButton(
            top_bar,
            text=f"📅 {date.today().isoformat()}",
            width=145,
            height=34,
            corner_radius=8,
            fg_color="#E0F2F1",
            text_color=PALETTE["primary"],
            hover_color="#B2DFDB",
            font=("Segoe UI", 12, "bold"),
        )
        btn_filtro_fecha.configure(
            command=lambda: VetCalendarModal(
                self,
                btn_filtro_fecha.cget("text").replace("📅 ", "").strip(),
                lambda d: [btn_filtro_fecha.configure(text=f"📅 {d}"), filtrar_dia()]
            )
        )
        btn_filtro_fecha.pack(side="left", padx=8)

        table_frame = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        table_frame.pack(fill="both", expand=True, padx=25, pady=10)

        cols = ("ID", "Hora", "Mascota", "Especie", "Dueño", "Teléfono", "Motivo", "Estado")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="Vet.Treeview")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=120, anchor="center")
        tree.pack(fill="both", expand=True, padx=15, pady=15)

        def filtrar_dia():
            self.sound.play_cat_meow()
            for i in tree.get_children():
                tree.delete(i)
            fecha_str = btn_filtro_fecha.cget("text").replace("📅 ", "").strip()
            for ci in self.repo.buscar_citas(fecha_exacta=fecha_str):
                tree.insert(
                    "",
                    "end",
                    values=(
                        ci["id"], ci["hora"], ci["mascota_nombre"], ci["especie"],
                        ci["dueno_nombre"], ci["dueno_telefono"], ci["motivo"], ci["estado"]
                    ),
                )

        ctk.CTkButton(top_bar, text="Consultar", fg_color=PALETTE["primary"], command=filtrar_dia).pack(
            side="left", padx=10
        )
        filtrar_dia()

    # --- VISTA 6: HISTORIAL DE MASCOTAS ATENDIDAS (RF-05) ---
    def vista_historial(self, parent: ctk.CTkFrame):
        ctk.CTkLabel(
            parent, text="Historial Clínico de Mascotas Atendidas (RF-05)", font=("Segoe UI", 24, "bold"), text_color=PALETTE["primary"]
        ).pack(anchor="w", padx=25, pady=(20, 10))

        table_frame = ctk.CTkFrame(parent, fg_color=PALETTE["card"], corner_radius=14)
        table_frame.pack(fill="both", expand=True, padx=25, pady=10)

        cols = ("Folio Cita", "Fecha", "Mascota", "Raza", "Dueño", "Servicio / Motivo", "Notas Clínicas")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings", style="Vet.Treeview")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=140, anchor="center")
        tree.pack(fill="both", expand=True, padx=15, pady=15)

        for ci in self.repo.buscar_citas(solo_atendidas=True):
            tree.insert(
                "",
                "end",
                values=(
                    f"PC-{ci['id']:05d}", ci["fecha"], ci["mascota_nombre"], ci["raza"],
                    ci["dueno_nombre"], ci["motivo"], ci.get("notas_clinicas") or "Atención completada"
                ),
            )


if __name__ == "__main__":
    app = PetCareApp()
    app.mainloop()