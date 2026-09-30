import customtkinter as ctk
from repositories import PetCareService
from sound_manager import SoundManager

BG_MAIN = "#0f172a"
BG_CARD = "#1e293b"
BORDER_SUBTLE = "#334155"
ROSE_PILL = "#f472b6"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

CATALOGO = {
    "Canino (Perro)": ["Mestizo / Criollo", "Labrador", "Golden Retriever", "Pastor Alemán", "Bulldog", "Pug", "Chihuahua", "Husky Siberiano", "Rottweiler", "Beagle", "Otro"],
    "Felino (Gato)": ["Común Europeo / Criollo", "Siamés", "Persa", "Maine Coon", "Bengalí", "Sphynx", "Ragdoll", "Otro"],
    "Ave": ["Periquito", "Canario", "Ninfa", "Agapornis", "Loro", "Otro"],
    "Conejo": ["Belier", "Cabeza de León", "Enano / Toy", "Rex", "Otro"],
    "Roedor": ["Hámster", "Cobaya / Cuy", "Chinchilla", "Rata Doméstica", "Otro"],
    "Reptil": ["Tortuga", "Gecko", "Dragón Barbudo", "Iguana", "Otro"],
    "Otra Especie": ["General / Mestizo", "Otro"]
}

class RegistrarMascotaView(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color="transparent")
        self.app = app_ref

        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=18, border_width=1, border_color=BORDER_SUBTLE, width=560)
        card.grid(row=0, column=0, pady=25, padx=20)
        card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(card, text="Expediente de Mascota 🐶", font=("Segoe UI", 16, "bold"), text_color=TEXT_MAIN).grid(row=0, column=0, columnspan=2, pady=(25, 15), padx=25, sticky="w")

        ctk.CTkLabel(card, text="Seleccionar Dueño:", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).grid(row=1, column=0, sticky="w", padx=25, pady=(10, 3))
        self.combo_dueno = ctk.CTkComboBox(card, width=480, height=36, corner_radius=10, state="readonly", fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.combo_dueno.grid(row=2, column=0, columnspan=2, padx=25, pady=(0, 12))

        ctk.CTkLabel(card, text="Nombre del Paciente:", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).grid(row=3, column=0, sticky="w", padx=25, pady=(5, 3))
        self.entry_nombre = ctk.CTkEntry(card, placeholder_text="Ej. Toby", width=225, height=36, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.entry_nombre.grid(row=4, column=0, padx=(25, 10), pady=(0, 12), sticky="w")

        ctk.CTkLabel(card, text="Especie:", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).grid(row=3, column=1, sticky="w", padx=10, pady=(5, 3))
        esp_lista = list(CATALOGO.keys())
        self.combo_especie = ctk.CTkComboBox(card, values=esp_lista, width=225, height=36, corner_radius=10, state="readonly", fg_color=BG_MAIN, border_color=BORDER_SUBTLE, command=self._on_especie_change)
        self.combo_especie.grid(row=4, column=1, padx=(10, 25), pady=(0, 12), sticky="w")
        self.combo_especie.set(esp_lista[0])

        ctk.CTkLabel(card, text="Raza:", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).grid(row=5, column=0, sticky="w", padx=25, pady=(5, 3))
        self.combo_raza = ctk.CTkComboBox(card, values=CATALOGO[esp_lista[0]], width=225, height=36, corner_radius=10, state="readonly", fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.combo_raza.grid(row=6, column=0, padx=(25, 10), pady=(0, 20), sticky="w")
        self.combo_raza.set(CATALOGO[esp_lista[0]][0])

        ctk.CTkLabel(card, text="Edad (Años):", font=("Segoe UI", 12, "bold"), text_color=TEXT_MUTED).grid(row=5, column=1, sticky="w", padx=10, pady=(5, 3))
        self.entry_edad = ctk.CTkEntry(card, placeholder_text="0", width=225, height=36, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.entry_edad.grid(row=6, column=1, padx=(10, 25), pady=(0, 20), sticky="w")

        ctk.CTkButton(card, text="Guardar Expediente", fg_color=ROSE_PILL, hover_color="#db2777", text_color="#0f172a", font=("Segoe UI", 13, "bold"), corner_radius=12, height=44, command=self._guardar).grid(row=7, column=0, columnspan=2, padx=25, pady=(0, 25), sticky="ew")

    def sincronizar(self):
        clientes = PetCareService.listar_clientes()
        opc = [f"{c['idCliente']} - {c['nombreCliente']} {c['aPaterno']}" for c in clientes]
        self.combo_dueno.configure(values=opc)
        if opc and not self.combo_dueno.get():
            self.combo_dueno.set(opc[0])

    def _on_especie_change(self, esp):
        razas = CATALOGO.get(esp, ["Otro"])
        self.combo_raza.configure(values=razas)
        self.combo_raza.set(razas[0])

    def _guardar(self):
        SoundManager.reproducir("click")
        d = self.combo_dueno.get()
        nom = self.entry_nombre.get().strip()
        esp = self.combo_especie.get().strip()
        raza = self.combo_raza.get().strip()
        ed_txt = self.entry_edad.get().strip()

        if not (d and nom and esp):
            SoundManager.reproducir("alerta")
            self.app.mostrar_toast("Completa dueño, nombre y especie", "error")
            return

        try:
            edad = int(ed_txt) if ed_txt else 0
            if edad < 0: raise ValueError
        except ValueError:
            SoundManager.reproducir("alerta")
            self.app.mostrar_toast("La edad debe ser un número entero (≥ 0)", "error")
            return

        cid = int(d.split(" - ")[0])
        PetCareService.crear_mascota(nom, esp, raza, edad, cid)
        self.entry_nombre.delete(0, "end")
        self.entry_edad.delete(0, "end")
        SoundManager.reproducir("exito")
        self.app.mostrar_toast("Paciente vinculado a la clínica", "exito")