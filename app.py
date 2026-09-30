import tkinter as tk
from datetime import datetime, date
import customtkinter as ctk
from tkcalendar import DateEntry

from database import DatabaseManager
from repositories import PetCareService
from sound_manager import SoundManager

from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.citas_dia_view import CitasDiaView
from views.historial_view import HistorialView
from views.agendar_cita_view import AgendarCitaView
from views.registrar_mascota_view import RegistrarMascotaView
from views.clientes_view import ClientesView

ctk.set_appearance_mode("Dark")

BG_MAIN = "#0f172a"
BG_SIDEBAR = "#1e293b"
BG_CARD = "#1e293b"
BORDER_SUBTLE = "#334155"
TEAL_ACCENT = "#2dd4bf"
TEAL_HOVER = "#14b8a6"
AMBER_PILL = "#fbbf24"
RED_DANGER = "#ef4444"
RED_HOVER = "#dc2626"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

HORARIOS_PERMITIDOS = [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in (0, 15, 30, 45)]

class PetCareModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PetCare • Plataforma Veterinaria Integral")
        self.geometry("1260x810")
        self.minsize(1120, 720)
        self.configure(fg_color=BG_MAIN)

        DatabaseManager.initialize()
        SoundManager.init()

        self.usuario_activo = None
        self._vista_actual = None
        self._toast_job = None

        self._iniciar_login()

    def _iniciar_login(self):
        self.login_view = LoginView(self, on_login_success=self._on_login_success)
        self.login_view.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _on_login_success(self, usuario):
        self.usuario_activo = usuario
        self.login_view.destroy()
        self._construir_interfaz_principal()

    def _construir_interfaz_principal(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar Fijo sin recálculo destructivo (elimina glitches de corte)
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=BG_SIDEBAR, border_width=1, border_color=BORDER_SUBTLE)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        brand_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        brand_box.pack(fill="x", padx=20, pady=(24, 20))
        ctk.CTkLabel(brand_box, text="🐾", font=("Segoe UI", 26)).pack(side="left", padx=(0, 10))
        textos = ctk.CTkFrame(brand_box, fg_color="transparent")
        textos.pack(side="left")
        ctk.CTkLabel(textos, text="PetCare", font=("Segoe UI", 19, "bold"), text_color=TEXT_MAIN).pack(anchor="w")
        rol_color = AMBER_PILL if self.usuario_activo['rol'] == 'Administrador' else TEAL_ACCENT
        ctk.CTkLabel(textos, text=f"ROL: {self.usuario_activo['rol'].upper()}", font=("Segoe UI", 9, "bold"), text_color=rol_color).pack(anchor="w")

        # Botones de Navegación con hover visual estático suave (Cero retraso/lag)
        self.nav_buttons = {}
        items = [
            ("dashboard", "📊", "Agenda General"),
            ("citas_dia", "📅", "Citas por Fecha (RF-07)"),
            ("historial", "🔍", "Historial Paciente (RF-05)"),
            ("citas", "📝", "Agendar Cita (RF-01)"),
            ("mascotas", "🐶", "Registrar Paciente (RF-03)"),
            ("clientes", "👥", "Directorio Dueños (RF-02)")
        ]

        for key, icon, label in items:
            btn = ctk.CTkButton(
                self.sidebar_frame, text=f"  {icon}   {label}", anchor="w", height=42, corner_radius=10,
                font=("Segoe UI", 12, "bold"), fg_color="transparent", text_color=TEXT_MUTED,
                hover_color="#334155", command=lambda k=key: self.seleccionar_vista(k)
            )
            btn.pack(fill="x", padx=14, pady=4)
            self.nav_buttons[key] = btn

        # Espaciador
        spacer = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        ctk.CTkButton(
            self.sidebar_frame, text="🚪  Cerrar Sesión", height=38, corner_radius=10,
            fg_color="#334155", hover_color="#475569", font=("Segoe UI", 11, "bold"),
            command=self._cerrar_sesion
        ).pack(fill="x", padx=14, pady=(5, 18))

        # 2. Contenedor de Vistas (con margen generoso para evitar recortes)
        self.views_container = ctk.CTkFrame(self, fg_color="transparent")
        self.views_container.grid(row=0, column=1, sticky="nsew", padx=30, pady=25)

        self.vistas = {
            "dashboard": DashboardView(self.views_container, self),
            "citas_dia": CitasDiaView(self.views_container, self),
            "historial": HistorialView(self.views_container, self),
            "citas": AgendarCitaView(self.views_container, self),
            "mascotas": RegistrarMascotaView(self.views_container, self),
            "clientes": ClientesView(self.views_container, self)
        }

        for frame in self.vistas.values():
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # 3. Toast y Modal interno
        self._crear_toast_notification()
        self._crear_overlay_modal_interno()

        self.seleccionar_vista("dashboard", instantaneo=True)

    def seleccionar_vista(self, nombre_vista, instantaneo=False):
        if self._vista_actual == nombre_vista:
            return

        if not instantaneo:
            SoundManager.reproducir("click")

        self.cerrar_modal_interno()

        for k, btn in self.nav_buttons.items():
            if k == nombre_vista:
                btn.configure(fg_color="#334155", text_color=TEXT_MAIN)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_MUTED)

        self._vista_actual = nombre_vista
        v = self.vistas[nombre_vista]
        v.tkraise()

        # Actualización reactiva por vista
        if hasattr(v, "cargar_datos"):
            v.cargar_datos()
        elif hasattr(v, "sincronizar"):
            v.sincronizar()

    def _cerrar_sesion(self):
        SoundManager.reproducir("click")
        self.sidebar_frame.destroy()
        self.views_container.destroy()
        self.overlay_modal.destroy()
        self.usuario_activo = None
        self._vista_actual = None
        self._iniciar_login()

    # =========================================================================
    # MODAL INTERNO COMPARTIDO
    # =========================================================================
    def _crear_overlay_modal_interno(self):
        self.overlay_modal = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        self.box_modal = ctk.CTkFrame(self.overlay_modal, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_SUBTLE)

    def cerrar_modal_interno(self):
        for w in self.box_modal.winfo_children():
            w.destroy()
        self.box_modal.place_forget()
        self.overlay_modal.place_forget()

    def _mostrar_modal_interno(self, ancho=480, alto=360):
        SoundManager.reproducir("modal")
        self.overlay_modal.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay_modal.tkraise()
        self.box_modal.configure(width=ancho, height=alto)
        self.box_modal.place(relx=0.5, rely=0.5, anchor="center")

    def abrir_modal_editar_cita(self, cid, f_act, h_act, mascota_nom):
        for w in self.box_modal.winfo_children(): w.destroy()

        top = ctk.CTkFrame(self.box_modal, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(top, text=f"Reprogramar Cita: {mascota_nom}", font=("Segoe UI", 16, "bold"), text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkButton(top, text="✕", width=32, height=32, fg_color="transparent", hover_color="#334155", font=("Segoe UI", 14, "bold"), command=self.cerrar_modal_interno).pack(side="right")

        body = ctk.CTkFrame(self.box_modal, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=10)

        ctk.CTkLabel(body, text="Nueva Fecha (Calendario):", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(5, 3))
        cal_c = ctk.CTkFrame(body, fg_color=BG_MAIN, corner_radius=10, border_width=1, border_color=BORDER_SUBTLE, height=38)
        cal_c.pack(fill="x", pady=(0, 15))
        cal_c.pack_propagate(False)

        cal = DateEntry(cal_c, width=18, background="#0f172a", foreground="#ffffff", headersbackground="#1e293b", headersforeground="#2dd4bf", selectbackground="#0284c7", selectforeground="#ffffff", date_pattern="yyyy-mm-dd", mindate=date.today(), font=("Segoe UI", 11))
        try: cal.set_date(datetime.strptime(f_act, "%Y-%m-%d").date())
        except Exception: pass
        cal.pack(fill="both", expand=True, padx=5, pady=4)

        ctk.CTkLabel(body, text="Nuevo Horario (08:00 - 19:45):", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 3))
        cb = ctk.CTkComboBox(body, values=HORARIOS_PERMITIDOS, height=38, corner_radius=10, state="readonly", fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        cb.pack(fill="x", pady=(0, 20))
        cb.set(h_act if h_act in HORARIOS_PERMITIDOS else HORARIOS_PERMITIDOS[0])

        def guardar():
            SoundManager.reproducir("click")
            fn, hn = cal.get_date().strftime("%Y-%m-%d"), cb.get()
            if cal.get_date() < date.today():
                SoundManager.reproducir("alerta")
                self.mostrar_toast("No se permiten fechas pasadas", "error")
                return
            PetCareService.actualizar_cita(cid, fn, hn)
            self.cerrar_modal_interno()
            self.vistas["dashboard"].cargar_datos()
            SoundManager.reproducir("exito")
            self.mostrar_toast("Cita modificada con éxito", "exito")

        ctk.CTkButton(body, text="Guardar Nueva Fecha y Hora", fg_color=TEAL_ACCENT, hover_color=TEAL_HOVER, text_color="#0f172a", font=("Segoe UI", 13, "bold"), height=42, corner_radius=12, command=guardar).pack(fill="x", pady=(5, 10))
        self._mostrar_modal_interno(ancho=460, alto=340)

    def abrir_modal_eliminar_cita(self, cid, m_nom):
        for w in self.box_modal.winfo_children(): w.destroy()

        top = ctk.CTkFrame(self.box_modal, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(top, text="Eliminar Cita", font=("Segoe UI", 16, "bold"), text_color=RED_DANGER).pack(side="left")
        ctk.CTkButton(top, text="✕", width=32, height=32, fg_color="transparent", hover_color="#334155", font=("Segoe UI", 14, "bold"), command=self.cerrar_modal_interno).pack(side="right")

        body = ctk.CTkFrame(self.box_modal, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=15)
        ctk.CTkLabel(body, text=f"¿Deseas eliminar la cita médica de {m_nom}?", font=("Segoe UI", 12), text_color=TEXT_MAIN).pack(pady=(10, 20))

        btn_box = ctk.CTkFrame(body, fg_color="transparent")
        btn_box.pack(fill="x")

        def eliminar():
            SoundManager.reproducir("click")
            PetCareService.eliminar_cita(cid)
            self.cerrar_modal_interno()
            self.vistas["dashboard"].cargar_datos()
            SoundManager.reproducir("alerta")
            self.mostrar_toast("Cita eliminada", "info")

        ctk.CTkButton(btn_box, text="Cancelar", fg_color="#334155", hover_color="#475569", width=140, height=38, command=self.cerrar_modal_interno).pack(side="left", padx=(10, 5))
        ctk.CTkButton(btn_box, text="Sí, Eliminar", fg_color=RED_DANGER, hover_color=RED_HOVER, width=140, height=38, command=eliminar).pack(side="right", padx=(5, 10))
        self._mostrar_modal_interno(ancho=420, alto=220)

    def abrir_modal_editar_cliente(self, cid, n, p, m):
        for w in self.box_modal.winfo_children(): w.destroy()

        top = ctk.CTkFrame(self.box_modal, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(top, text="Modificar Datos del Propietario", font=("Segoe UI", 16, "bold"), text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkButton(top, text="✕", width=32, height=32, fg_color="transparent", hover_color="#334155", font=("Segoe UI", 14, "bold"), command=self.cerrar_modal_interno).pack(side="right")

        body = ctk.CTkFrame(self.box_modal, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=10)

        ctk.CTkLabel(body, text="Nombre(s):", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(5, 2))
        en = ctk.CTkEntry(body, height=36, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        en.pack(fill="x", pady=(0, 10)); en.insert(0, n)

        ctk.CTkLabel(body, text="Apellido Paterno:", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        ep = ctk.CTkEntry(body, height=36, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        ep.pack(fill="x", pady=(0, 10)); ep.insert(0, p)

        ctk.CTkLabel(body, text="Apellido Materno (Opcional):", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 2))
        em = ctk.CTkEntry(body, height=36, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        em.pack(fill="x", pady=(0, 18)); em.insert(0, m)

        def guardar():
            SoundManager.reproducir("click")
            n1, p1, m1 = en.get().strip(), ep.get().strip(), em.get().strip()
            if not n1 or not p1:
                SoundManager.reproducir("alerta")
                self.mostrar_toast("Nombre y Paterno son requeridos", "error")
                return
            PetCareService.actualizar_cliente(cid, n1, p1, m1)
            self.cerrar_modal_interno()
            self.vistas["clientes"].cargar_datos()
            SoundManager.reproducir("exito")
            self.mostrar_toast("Datos actualizados", "exito")

        ctk.CTkButton(body, text="Guardar Cambios", fg_color=TEAL_ACCENT, hover_color=TEAL_HOVER, text_color="#0f172a", font=("Segoe UI", 13, "bold"), height=42, corner_radius=12, command=guardar).pack(fill="x", pady=(5, 10))
        self._mostrar_modal_interno(ancho=440, alto=380)

    def abrir_modal_eliminar_cliente(self, cid, nom):
        for w in self.box_modal.winfo_children(): w.destroy()

        top = ctk.CTkFrame(self.box_modal, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(top, text="Eliminar Propietario", font=("Segoe UI", 16, "bold"), text_color=RED_DANGER).pack(side="left")
        ctk.CTkButton(top, text="✕", width=32, height=32, fg_color="transparent", hover_color="#334155", font=("Segoe UI", 14, "bold"), command=self.cerrar_modal_interno).pack(side="right")

        body = ctk.CTkFrame(self.box_modal, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=15)
        ctk.CTkLabel(body, text=f"¿Eliminar a {nom}?\nSe borrarán todas sus mascotas y citas asociadas.", font=("Segoe UI", 12), text_color=TEXT_MAIN).pack(pady=(10, 20))

        btn_box = ctk.CTkFrame(body, fg_color="transparent")
        btn_box.pack(fill="x")

        def eliminar():
            SoundManager.reproducir("click")
            PetCareService.eliminar_cliente(cid)
            self.cerrar_modal_interno()
            self.vistas["clientes"].cargar_datos()
            SoundManager.reproducir("alerta")
            self.mostrar_toast("Propietario eliminado", "info")

        ctk.CTkButton(btn_box, text="Cancelar", fg_color="#334155", hover_color="#475569", width=140, height=38, command=self.cerrar_modal_interno).pack(side="left", padx=(10, 5))
        ctk.CTkButton(btn_box, text="Sí, Eliminar", fg_color=RED_DANGER, hover_color=RED_HOVER, width=140, height=38, command=eliminar).pack(side="right", padx=(5, 10))
        self._mostrar_modal_interno(ancho=420, alto=230)

    # Toast
    def _crear_toast_notification(self):
        self.toast = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=12, border_width=1, border_color=BORDER_SUBTLE)
        self.toast_label = ctk.CTkLabel(self.toast, text="", font=("Segoe UI", 11, "bold"), text_color=TEXT_MAIN)
        self.toast_label.pack(padx=20, pady=12)

    def mostrar_toast(self, mensaje, tipo="info"):
        colores = {
            "info": ("#0ea5e9", "#7dd3fc"),
            "exito": (TEAL_HOVER, TEAL_ACCENT),
            "error": ("#e11d48", "#fda4af")
        }
        borde, texto_color = colores.get(tipo, colores["info"])
        self.toast.configure(border_color=borde)
        self.toast_label.configure(text=mensaje, text_color=texto_color)

        self.toast.place(relx=0.97, rely=0.94, anchor="se")
        self.toast.tkraise()
        if self._toast_job:
            self.after_cancel(self._toast_job)
        self._toast_job = self.after(3000, self.toast.place_forget)

if __name__ == "__main__":
    app = PetCareModernApp()
    app.mainloop()