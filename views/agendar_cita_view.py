from datetime import date
import customtkinter as ctk
from tkcalendar import DateEntry
from repositories import PetCareService
from sound_manager import SoundManager

BG_MAIN = "#0f172a"
BG_CARD = "#1e293b"
BORDER_SUBTLE = "#334155"
TEAL_ACCENT = "#2dd4bf"
TEAL_HOVER = "#14b8a6"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

HORARIOS_PERMITIDOS = [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in (0, 15, 30, 45)]

class AgendarCitaView(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color="transparent")
        self.app = app_ref

        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_SUBTLE, width=560)
        card.grid(row=0, column=0, pady=25, padx=20)
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(card, text="Programar Consulta Médica 🩺", font=("Segoe UI", 16, "bold"), text_color=TEXT_MAIN).grid(row=0, column=0, columnspan=2, pady=(25, 15), padx=25, sticky="w")

        ctk.CTkLabel(card, text="Dueño / Cliente:", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).grid(row=1, column=0, sticky="w", padx=25, pady=(10, 3))
        self.combo_dueno = ctk.CTkComboBox(card, width=480, height=36, corner_radius=10, state="readonly", fg_color=BG_MAIN, border_color=BORDER_SUBTLE, command=self._on_dueno_change)
        self.combo_dueno.grid(row=2, column=0, columnspan=2, padx=25, pady=(0, 10))

        ctk.CTkLabel(card, text="Paciente (Mascota):", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).grid(row=3, column=0, sticky="w", padx=25, pady=(10, 3))
        self.combo_mascota = ctk.CTkComboBox(card, width=480, height=36, corner_radius=10, state="readonly", fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.combo_mascota.grid(row=4, column=0, columnspan=2, padx=25, pady=(0, 10))

        ctk.CTkLabel(card, text="Fecha de Cita (Calendario):", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).grid(row=5, column=0, sticky="w", padx=25, pady=(10, 3))
        cal_c = ctk.CTkFrame(card, fg_color=BG_MAIN, corner_radius=10, border_width=1, border_color=BORDER_SUBTLE, width=225, height=36)
        cal_c.grid(row=6, column=0, padx=(25, 10), pady=(0, 20), sticky="w")
        cal_c.pack_propagate(False)

        self.cal_fecha = DateEntry(
            cal_c, width=18, background="#0f172a", foreground="#ffffff",
            headersbackground="#1e293b", headersforeground="#2dd4bf",
            selectbackground="#0284c7", selectforeground="#ffffff",
            date_pattern="yyyy-mm-dd", mindate=date.today(), font=("Segoe UI", 11)
        )
        self.cal_fecha.pack(fill="both", expand=True, padx=4, pady=4)

        ctk.CTkLabel(card, text="Horario Permitido (08:00 - 19:45):", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).grid(row=5, column=1, sticky="w", padx=10, pady=(10, 3))
        self.combo_hora = ctk.CTkComboBox(card, values=HORARIOS_PERMITIDOS, width=225, height=36, corner_radius=10, state="readonly", fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.combo_hora.grid(row=6, column=1, padx=(10, 25), pady=(0, 20), sticky="w")
        self.combo_hora.set(HORARIOS_PERMITIDOS[0])

        ctk.CTkButton(card, text="Confirmar y Agendar Cita", fg_color=TEAL_ACCENT, hover_color=TEAL_HOVER, text_color="#0f172a", font=("Segoe UI", 13, "bold"), corner_radius=12, height=44, command=self._guardar).grid(row=7, column=0, columnspan=2, padx=25, pady=(0, 25), sticky="ew")

    def sincronizar(self):
        clientes = PetCareService.listar_clientes()
        opciones = [f"{c['idCliente']} - {c['nombreCliente']} {c['aPaterno']}" for c in clientes]
        self.combo_dueno.configure(values=opciones)
        if opciones:
            if not self.combo_dueno.get(): self.combo_dueno.set(opciones[0])
            self._on_dueno_change(self.combo_dueno.get())

    def _on_dueno_change(self, sel):
        if not sel: return
        cid = int(sel.split(" - ")[0])
        mascotas = PetCareService.listar_mascotas_por_cliente(cid)
        opc_m = [f"{m['idMascota']} - {m['nombreMascota']} ({m['especie']})" for m in mascotas]
        self.combo_mascota.configure(values=opc_m)
        self.combo_mascota.set(opc_m[0] if opc_m else "Sin pacientes registrados")

    def _guardar(self):
        SoundManager.reproducir("click")
        d = self.combo_dueno.get()
        m = self.combo_mascota.get()
        f_str = self.cal_fecha.get_date().strftime("%Y-%m-%d")
        h = self.combo_hora.get().strip()

        if not (d and m and f_str and h) or m == "Sin pacientes registrados":
            SoundManager.reproducir("alerta")
            self.app.mostrar_toast("Completa todos los campos", "error")
            return

        if self.cal_fecha.get_date() < date.today():
            SoundManager.reproducir("alerta")
            self.app.mostrar_toast("No puedes agendar en fechas pasadas", "error")
            return

        cid = int(d.split(" - ")[0])
        mid = int(m.split(" - ")[0])
        PetCareService.crear_cita(f_str, h, mid, cid)
        SoundManager.reproducir("exito")
        self.app.mostrar_toast(f"Cita confirmada: {f_str} {h}", "exito")