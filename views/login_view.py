import customtkinter as ctk
from repositories import PetCareService
from sound_manager import SoundManager

BG_MAIN = "#0f172a"
BG_CARD = "#1e293b"
BORDER_SUBTLE = "#334155"
TEAL_ACCENT = "#2dd4bf"
TEAL_HOVER = "#14b8a6"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=BG_MAIN)
        self.on_login_success = on_login_success

        SoundManager.reproducir_musica_bienvenida("bienvenida.mp3")

        box = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=20, border_width=1, border_color=BORDER_SUBTLE, width=440, height=490)
        box.place(relx=0.5, rely=0.5, anchor="center")
        box.pack_propagate(False)

        ctk.CTkLabel(box, text="🐾", font=("Segoe UI", 40)).pack(pady=(35, 5))
        ctk.CTkLabel(box, text="PetCare System", font=("Segoe UI", 22, "bold"), text_color=TEXT_MAIN).pack()
        ctk.CTkLabel(box, text="Control de Acceso & Permisos (RF-06)", font=("Segoe UI", 11), text_color=TEAL_ACCENT).pack(pady=(0, 25))

        self.user_entry = ctk.CTkEntry(box, placeholder_text="Usuario (admin o staff)", width=320, height=42, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.user_entry.pack(pady=8)
        self.user_entry.insert(0, "admin")

        self.pass_entry = ctk.CTkEntry(box, placeholder_text="Contraseña", width=320, height=42, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE, show="•")
        self.pass_entry.pack(pady=8)
        self.pass_entry.insert(0, "admin123")
        self.pass_entry.bind("<Return>", lambda e: self._intentar_login())

        btn_login = ctk.CTkButton(box, text="Iniciar Sesión", width=320, height=44, corner_radius=12, fg_color=TEAL_ACCENT, hover_color=TEAL_HOVER, text_color="#0f172a", font=("Segoe UI", 13, "bold"), command=self._intentar_login)
        btn_login.pack(pady=(20, 15))

        ctk.CTkLabel(box, text="Demo Admin: admin / admin123\nDemo Personal: staff / staff123", font=("Segoe UI", 10), text_color=TEXT_MUTED).pack()

    def _intentar_login(self):
        SoundManager.reproducir("click")
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()

        usuario = PetCareService.autenticar(u, p)
        if not usuario:
            SoundManager.reproducir("alerta")
            err = ctk.CTkFrame(self, fg_color="#7f1d1d", corner_radius=8)
            err.place(relx=0.5, rely=0.88, anchor="center")
            ctk.CTkLabel(err, text="Usuario o contraseña incorrectos", font=("Segoe UI", 11, "bold"), text_color="#fca5a5").pack(padx=20, pady=8)
            self.after(2200, err.destroy)
            return

        SoundManager.detener_musica(fade_ms=500)
        SoundManager.reproducir("exito")
        self.on_login_success(usuario)