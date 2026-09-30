import sqlite3

DB_PATH = "petcare_enterprise.db"

class DatabaseManager:
    @staticmethod
    def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def initialize():
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            
            # RF-06: Control de permisos y usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuario (
                    idUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    nombreCompleto TEXT NOT NULL,
                    rol TEXT NOT NULL CHECK(rol IN ('Administrador', 'Personal'))
                )
            """)

            # RF-02: Clientes / Propietarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cliente (
                    idCliente INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombreCliente TEXT NOT NULL,
                    aPaterno TEXT NOT NULL,
                    aMaterno TEXT,
                    fechaRegistro TEXT NOT NULL
                )
            """)
            
            # RF-03: Mascotas / Pacientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mascota (
                    idMascota INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombreMascota TEXT NOT NULL,
                    especie TEXT NOT NULL,
                    raza TEXT,
                    edad INTEGER DEFAULT 0 CHECK(edad >= 0),
                    idCliente INTEGER NOT NULL,
                    FOREIGN KEY (idCliente) REFERENCES cliente (idCliente) ON DELETE CASCADE
                )
            """)
            
            # RF-01 / RF-07: Citas médicas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cita (
                    idCita INTEGER PRIMARY KEY AUTOINCREMENT,
                    fechaCita TEXT NOT NULL,
                    horaCita TEXT NOT NULL,
                    idMascota INTEGER NOT NULL,
                    idCliente INTEGER NOT NULL,
                    FOREIGN KEY (idMascota) REFERENCES mascota (idMascota) ON DELETE CASCADE,
                    FOREIGN KEY (idCliente) REFERENCES cliente (idCliente) ON DELETE CASCADE
                )
            """)

            # Usuarios iniciales para pruebas
            cursor.execute("SELECT COUNT(*) FROM usuario")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO usuario (username, password, nombreCompleto, rol)
                    VALUES 
                    ('admin', 'admin123', 'Administrador General', 'Administrador'),
                    ('staff', 'staff123', 'Personal Veterinario', 'Personal')
                """)

            conn.commit()