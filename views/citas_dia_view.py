import customtkinter as ctk
from tkcalendar import DateEntry
from repositories import PetCareService
from sound_manager import SoundManager

BG_MAIN = "#0f172a"
BG_CARD = "#1e293b"
BG_ITEM_CARD = "#172236"
BORDER_SUBTLE = "#334155"
TEAL_ACCENT = "#2dd4bf"
TEAL_HOVER = "#14b8a6"
AMBER_PILL = "#fbbf24"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

class CitasDiaView(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color="transparent")
        self.app = app_ref

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_SUBTLE)
        top_box.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)

        ctk.CTkLabel(top_box, text="Citas Programadas (RF-07) 📅", font=("Segoe UI", 16, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(top_box, text="Selecciona fecha:", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).pack(side="left", padx=(15, 8))

        cal_box = ctk.CTkFrame(top_box, fg_color=BG_MAIN, corner_radius=10, border_width=1, border_color=BORDER_SUBTLE, width=200, height=36)
        cal_box.pack(side="left", padx=5)
        cal_box.pack_propagate(False)

        self.cal_rf07 = DateEntry(
            cal_box, width=16, background="#0f172a", foreground="#ffffff",
            headersbackground="#1e293b", headersforeground="#2dd4bf",
            selectbackground="#0284c7", selectforeground="#ffffff",
            date_pattern="yyyy-mm-dd", font=("Segoe UI", 11)
        )
        self.cal_rf07.pack(fill="both", expand=True, padx=4, pady=4)
        self.cal_rf07.bind("<<DateEntrySelected>>", lambda e: self.cargar_datos())

        ctk.CTkButton(top_box, text="Consultar Agenda", width=130, height=36, corner_radius=10, fg_color=TEAL_ACCENT, hover_color=TEAL_HOVER, text_color="#0f172a", font=("Segoe UI", 13, "bold"), command=self.cargar_datos).pack(side="left", padx=15)

        res_box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_SUBTLE)
        res_box.grid(row=1, column=0, sticky="nsew", padx=5)
        res_box.grid_columnconfigure(0, weight=1)
        res_box.grid_rowconfigure(0, weight=1)

        self.scroll_citas = ctk.CTkScrollableFrame(res_box, fg_color="transparent", corner_radius=12)
        self.scroll_citas.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)

    def cargar_datos(self):
        SoundManager.reproducir("click")
        for widget in self.scroll_citas.winfo_children():
            widget.destroy()

        fecha_sel = self.cal_rf07.get_date().strftime("%Y-%m-%d")
        citas = PetCareService.obtener_citas_por_fecha(fecha_sel)

        if not citas:
            ctk.CTkLabel(self.scroll_citas, text=f"No hay citas programadas para el {fecha_sel}.", font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(pady=60)
            return

        for r in citas:
            card = ctk.CTkFrame(self.scroll_citas, fg_color=BG_ITEM_CARD, corner_radius=14, border_width=1, border_color=BORDER_SUBTLE)
            card.pack(fill="x", pady=6, padx=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=18, pady=12)

            col_izq = ctk.CTkFrame(inner, fg_color="transparent")
            col_izq.pack(side="left")
            ctk.CTkLabel(col_izq, text=f"🐾  {r['nombreMascota']}", font=("Segoe UI", 15, "bold"), text_color=TEXT_MAIN).pack(anchor="w")
            ctk.CTkLabel(col_izq, text=f"Dueño: {r['nomDueno']} • {r['especie']} ({r['raza']})", font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(anchor="w")

            bh = ctk.CTkFrame(inner, fg_color="#1e293b", corner_radius=8, border_width=1, border_color="#f59e0b")
            bh.pack(side="right")
            ctk.CTkLabel(bh, text=f"⏰  {r['horaCita']}", font=("Segoe UI", 12, "bold"), text_color=AMBER_PILL).pack(padx=12, pady=6)