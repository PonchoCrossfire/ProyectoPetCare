import tkinter as tk
import customtkinter as ctk
from repositories import PetCareService
from sound_manager import SoundManager

BG_MAIN = "#0f172a"
BG_CARD = "#1e293b"
BG_ITEM_CARD = "#172236"
BORDER_SUBTLE = "#334155"
TEAL_ACCENT = "#2dd4bf"
TEAL_HOVER = "#14b8a6"
RED_HOVER = "#dc2626"
TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

class ClientesView(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color="transparent")
        self.app = app_ref

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        form = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_SUBTLE)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 15), padx=5)

        ctk.CTkLabel(form, text="Nuevo Dueño:", font=("Segoe UI", 12, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=16, pady=16)

        self.e_nom = ctk.CTkEntry(form, placeholder_text="Nombre(s)", width=160, height=36, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.e_nom.pack(side="left", padx=5, pady=16)

        self.e_pat = ctk.CTkEntry(form, placeholder_text="A. Paterno", width=160, height=36, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.e_pat.pack(side="left", padx=5, pady=16)

        self.e_mat = ctk.CTkEntry(form, placeholder_text="A. Materno", width=160, height=36, corner_radius=10, fg_color=BG_MAIN, border_color=BORDER_SUBTLE)
        self.e_mat.pack(side="left", padx=5, pady=16)

        ctk.CTkButton(form, text="+ Registrar", fg_color=TEAL_ACCENT, hover_color=TEAL_HOVER, text_color="#0f172a", font=("Segoe UI", 13, "bold"), corner_radius=10, width=120, height=36, command=self._guardar).pack(side="left", padx=15, pady=16)

        table_card = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=16, border_width=1, border_color=BORDER_SUBTLE)
        table_card.grid(row=1, column=0, sticky="nsew", padx=5)
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(0, weight=1)

        self.scroll_clientes = ctk.CTkScrollableFrame(table_card, fg_color="transparent", corner_radius=12)
        self.scroll_clientes.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

    def cargar_datos(self):
        for w in self.scroll_clientes.winfo_children(): w.destroy()
        clientes = PetCareService.listar_clientes()
        if not clientes:
            ctk.CTkLabel(self.scroll_clientes, text="No hay clientes registrados aún.", font=("Segoe UI", 13), text_color=TEXT_MUTED).pack(pady=50)
            return

        es_admin = self.app.usuario_activo and self.app.usuario_activo.get("rol") == "Administrador"

        for c in clientes:
            cid = int(c["idCliente"])
            n, p = str(c["nombreCliente"]), str(c["aPaterno"])
            m = str(c["aMaterno"]) if c["aMaterno"] else ""

            card = ctk.CTkFrame(self.scroll_clientes, fg_color=BG_ITEM_CARD, corner_radius=14, border_width=1, border_color=BORDER_SUBTLE)
            card.pack(fill="x", pady=8, padx=6)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=18, pady=14)

            col_izq = ctk.CTkFrame(inner, fg_color="transparent")
            col_izq.pack(side="left")
            ctk.CTkLabel(col_izq, text=f"👤  {n} {p} {m}".strip(), font=("Segoe UI", 15, "bold"), text_color=TEXT_MAIN).pack(anchor="w")
            ctk.CTkLabel(col_izq, text=f"Código: #{cid}  •  Alta: {c['fechaRegistro']}", font=("Segoe UI", 11), text_color=TEXT_MUTED).pack(anchor="w", pady=(2, 0))

            col_der = ctk.CTkFrame(inner, fg_color="transparent")
            col_der.pack(side="right")

            ctk.CTkButton(col_der, text="✏️ Editar", width=75, height=32, corner_radius=8, font=("Segoe UI", 11, "bold"), fg_color="#334155", hover_color="#475569", command=lambda i=cid, n1=n, p1=p, m1=m: self.app.abrir_modal_editar_cliente(i, n1, p1, m1)).pack(side="left", padx=4)

            if es_admin:
                ctk.CTkButton(col_der, text="🗑️", width=38, height=32, corner_radius=8, font=("Segoe UI", 12, "bold"), fg_color="#7f1d1d", hover_color=RED_HOVER, command=lambda i=cid, n1=n: self.app.abrir_modal_eliminar_cliente(i, n1)).pack(side="left", padx=4)

            self._bind_context_menu(card, cid, n, p, m, es_admin)

    def _bind_context_menu(self, widget, cid, n, p, m, es_admin):
        def pop(e):
            SoundManager.reproducir("click")
            menu = tk.Menu(self, tearoff=0, bg="#1e293b", fg="#ffffff", activebackground="#0284c7", activeforeground="#ffffff", font=("Segoe UI", 10))
            menu.add_command(label=f"✏️ Editar Propietario ({n})", command=lambda: self.app.abrir_modal_editar_cliente(cid, n, p, m))
            if es_admin:
                menu.add_separator()
                menu.add_command(label="🗑️ Eliminar Propietario", command=lambda: self.app.abrir_modal_eliminar_cliente(cid, n))
            menu.post(e.x_root, e.y_root)
        widget.bind("<Button-3>", pop)

    def _guardar(self):
        SoundManager.reproducir("click")
        n = self.e_nom.get().strip()
        p = self.e_pat.get().strip()
        m = self.e_mat.get().strip()
        if not n or not p:
            SoundManager.reproducir("alerta")
            self.app.mostrar_toast("Nombre y Apellido requeridos", "error")
            return
        PetCareService.crear_cliente(n, p, m)
        self.e_nom.delete(0, "end")
        self.e_pat.delete(0, "end")
        self.e_mat.delete(0, "end")
        self.cargar_datos()
        SoundManager.reproducir("exito")
        self.app.mostrar_toast("Propietario registrado exitosamente", "exito")