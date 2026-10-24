import sqlite3
from contextlib import contextmanager

DB_NAME = "petcare_enterprise.db"


class DatabaseManager:
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self._init_db()

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # RF-06: Control de permisos y cuentas de usuario
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    rol TEXT NOT NULL CHECK(rol IN ('admin', 'recepcionista'))
                )
            """)

            # RF-02, RF-08, RF-09: Clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    domicilio TEXT NOT NULL,
                    telefono TEXT NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # RF-03, RF-08, RF-09: Mascotas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mascotas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    nombre TEXT NOT NULL,
                    especie TEXT NOT NULL DEFAULT 'Perro',
                    raza TEXT NOT NULL,
                    edad TEXT NOT NULL,
                    alergias TEXT DEFAULT 'Ninguna',
                    vacunas TEXT DEFAULT 'Al día',
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
                )
            """)

            # RF-01, RF-04, RF-05, RF-07, RF-10: Citas y Seguimiento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS citas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mascota_id INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    motivo TEXT NOT NULL,
                    estado TEXT NOT NULL DEFAULT 'Programada' 
                        CHECK(estado IN ('Programada', 'Atendida', 'Cancelada')),
                    notas_clinicas TEXT DEFAULT '',
                    FOREIGN KEY (mascota_id) REFERENCES mascotas(id) ON DELETE CASCADE
                )
            """)

            # Semilla de usuarios por defecto
            cursor.execute("SELECT COUNT(*) as total FROM usuarios")
            if cursor.fetchone()["total"] == 0:
                cursor.executemany(
                    "INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
                    [
                        ("admin", "admin123", "admin"),
                        ("recepcion", "vet123", "recepcionista"),
                    ],
                )