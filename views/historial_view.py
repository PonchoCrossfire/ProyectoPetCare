import customtkinter as ctk
from repositories import PetCareService
from sound_manager import SoundManager

BG_MAIN = "#0f172a"
BG_CARD = "#1e293b"
BG_ITEM_CARD = "#172236"
BORDER_SUBTLE = "#334155"
TEAL_ACCENT = "#2dd4bf"
TEAL_HOVER = "#14b8a6"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

class HistorialView(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color="transparent")
        self.app = app_ref

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        top_box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_SUBTLE)
        top_box.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)

        ctk.CTkLabel(top_box, text="Expediente Clínico (RF-05) 🔍", font=("Segoe UI", 16, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=20, pady=15)

        self.entry_busqueda = ctk.CTkEntry(top_box, placeholder_text="Digita el nombre de la mascota...", width=260, height=36, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.entry_busqueda.pack(side="left", padx=10)
        self.entry_busqueda.bind("<Return>", lambda e: self._buscar())

        ctk.CTkButton(top_box, text="Buscar Paciente", width=130, height=36, corner_radius=10, fg_color=TEAL_ACCENT, hover_color=TEAL_HOVER, text_color="#0f172a", font=("Segoe UI", 13, "bold"), command=self._buscar).pack(side="left", padx=10)

        split_box = ctk.CTkFrame(self, fg_color="transparent")
        split_box.grid(row=1, column=0, sticky="nsew", padx=5)
        split_box.grid_columnconfigure(0, weight=1)
        split_box.grid_columnconfigure(1, weight=1)
        split_box.grid_rowconfigure(0, weight=1)

        p_izq = ctk.CTkFrame(split_box, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_SUBTLE)
        p_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        p_izq.grid_columnconfigure(0, weight=1)
        p_izq.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(p_izq, text="Mascotas Encontradas", font=("Segoe UI", 15, "bold"), text_color=TEXT_MAIN).grid(row=0, column=0, sticky="w", padx=18, pady=15)
        self.scroll_mascotas = ctk.CTkScrollableFrame(p_izq, fg_color="transparent")
        self.scroll_mascotas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        p_der = ctk.CTkFrame(split_box, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_SUBTLE)
        p_der.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        p_der.grid_columnconfigure(0, weight=1)
        p_der.grid_rowconfigure(1, weight=1)
        self.lbl_detalle = ctk.CTkLabel(p_der, text="Historial de Citas del Paciente", font=("Segoe UI", 15, "bold"), text_color=TEXT_MAIN)
        self.lbl_detalle.grid(row=0, column=0, sticky="w", padx=18, pady=15)
        self.scroll_citas = ctk.CTkScrollableFrame(p_der, fg_color="transparent")
        self.scroll_citas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

    def _buscar(self):
        SoundManager.reproducir("click")
        for w in self.scroll_mascotas.winfo_children(): w.destroy()
        for w in self.scroll_citas.winfo_children(): w.destroy()

        t = self.entry_busqueda.get().strip()
        if not t:
            SoundManager.reproducir("alerta")
            self.app.mostrar_toast("Digita el nombre de una mascota", "error")
            return

        mascotas = PetCareService.buscar_mascotas_por_nombre(t)
        if not mascotas:
            ctk.CTkLabel(self.scroll_mascotas, text="No se encontraron pacientes.", font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(pady=30)
            return

        for m in mascotas:
            card = ctk.CTkFrame(self.scroll_mascotas, fg_color=BG_ITEM_CARD, corner_radius=12, border_width=1, border_color=BORDER_SUBTLE)
            card.pack(fill="x", pady=5, padx=2)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            col = ctk.CTkFrame(inner, fg_color="transparent")
            col.pack(side="left")
            ctk.CTkLabel(col, text=f"🐾 {m['nombreMascota']}", font=("Segoe UI", 14, "bold"), text_color=TEXT_MAIN).pack(anchor="w")
            ctk.CTkLabel(col, text=f"Dueño: {m['nomDueno']} • {m['especie']} ({m['edad']} años)", font=("Segoe UI", 11), text_color=TEXT_MUTED).pack(anchor="w")

            ctk.CTkButton(
                inner, text="Ver Citas ➔", width=90, height=32, corner_radius=8, fg_color="#334155", hover_color="#475569", font=("Segoe UI", 11, "bold"),
                command=lambda mid=m['idMascota'], nom=m['nombreMascota']: self._desplegar_citas(mid, nom)
            ).pack(side="right")

    def _desplegar_citas(self, id_mascota, nombre):
        SoundManager.reproducir("click")
        for w in self.scroll_citas.winfo_children(): w.destroy()
        self.lbl_detalle.configure(text=f"Historial de Citas: {nombre}")

        citas = PetCareService.obtener_historial_citas_mascota(id_mascota)
        if not citas:
            ctk.CTkLabel(self.scroll_citas, text="Este paciente aún no tiene citas.", font=("Segoe UI", 12), text_color=TEXT_MUTED).pack(pady=40)
            return

        for c in citas:
            card = ctk.CTkFrame(self.scroll_citas, fg_color=BG_ITEM_CARD, corner_radius=12, border_width=1, border_color=BORDER_SUBTLE)
            card.pack(fill="x", pady=5, padx=2)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=14, pady=10)

            ctk.CTkLabel(inner, text=f"Cita #{c['idCita']}", font=("Segoe UI", 12, "bold"), text_color=TEXT_MAIN).pack(side="left")
            ctk.CTkLabel(inner, text=f"📅 {c['fechaCita']}   ⏰ {c['horaCita']}", font=("Segoe UI", 11, "bold"), text_color=TEAL_ACCENT).pack(side="right")