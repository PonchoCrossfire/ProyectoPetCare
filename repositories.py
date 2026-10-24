from database import DatabaseManager


class PetCareRepository:
    def __init__(self, db: DatabaseManager):
        self.db = db

    # --- AUTENTICACIÓN (RF-06) ---
    def autenticar(self, username: str, password: str):
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "SELECT id, username, rol FROM usuarios WHERE username = ? AND password = ?",
                (username.strip(), password.strip()),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    # --- CLIENTES (RF-02, RF-08, RF-09) ---
    def crear_cliente(self, nombre: str, domicilio: str, telefono: str) -> int:
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO clientes (nombre, domicilio, telefono) VALUES (?, ?, ?)",
                (nombre.strip(), domicilio.strip(), telefono.strip()),
            )
            return cur.lastrowid

    def actualizar_cliente(self, cliente_id: int, nombre: str, domicilio: str, telefono: str):
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE clientes SET nombre = ?, domicilio = ?, telefono = ? WHERE id = ?",
                (nombre.strip(), domicilio.strip(), telefono.strip(), cliente_id),
            )

    def eliminar_cliente(self, cliente_id: int):
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))

    def listar_clientes(self, filtro: str = ""):
        with self.db.get_connection() as conn:
            if filtro:
                q = f"%{filtro.strip()}%"
                cur = conn.execute(
                    "SELECT * FROM clientes WHERE nombre LIKE ? OR telefono LIKE ? ORDER BY id DESC",
                    (q, q),
                )
            else:
                cur = conn.execute("SELECT * FROM clientes ORDER BY id DESC")
            return [dict(r) for r in cur.fetchall()]

    # --- MASCOTAS (RF-03, RF-08, RF-09) ---
    def crear_mascota(self, cliente_id: int, nombre: str, especie: str, raza: str, edad: str, alergias: str, vacunas: str) -> int:
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """INSERT INTO mascotas (cliente_id, nombre, especie, raza, edad, alergias, vacunas)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (cliente_id, nombre.strip(), especie, raza.strip(), edad.strip(), alergias.strip(), vacunas.strip()),
            )
            return cur.lastrowid

    def actualizar_mascota(self, mascota_id: int, cliente_id: int, nombre: str, especie: str, raza: str, edad: str, alergias: str, vacunas: str):
        with self.db.get_connection() as conn:
            conn.execute(
                """UPDATE mascotas 
                   SET cliente_id=?, nombre=?, especie=?, raza=?, edad=?, alergias=?, vacunas=?
                   WHERE id=?""",
                (cliente_id, nombre.strip(), especie, raza.strip(), edad.strip(), alergias.strip(), vacunas.strip(), mascota_id),
            )

    def eliminar_mascota(self, mascota_id: int):
        with self.db.get_connection() as conn:
            conn.execute("DELETE FROM mascotas WHERE id = ?", (mascota_id,))

    def listar_mascotas(self, filtro: str = ""):
        with self.db.get_connection() as conn:
            base_sql = """
                SELECT m.*, c.nombre AS dueno_nombre, c.telefono AS dueno_telefono, c.domicilio AS dueno_domicilio
                FROM mascotas m
                JOIN clientes c ON m.cliente_id = c.id
            """
            if filtro:
                q = f"%{filtro.strip()}%"
                cur = conn.execute(
                    base_sql + " WHERE m.nombre LIKE ? OR c.nombre LIKE ? OR m.raza LIKE ? ORDER BY m.id DESC",
                    (q, q, q),
                )
            else:
                cur = conn.execute(base_sql + " ORDER BY m.id DESC")
            return [dict(r) for r in cur.fetchall()]

    # --- CITAS E HISTORIAL (RF-01, RF-04, RF-05, RF-07, RF-10) ---
    def agendar_cita(self, mascota_id: int, fecha: str, hora: str, motivo: str) -> int:
        with self.db.get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO citas (mascota_id, fecha, hora, motivo, estado) VALUES (?, ?, ?, ?, 'Programada')",
                (mascota_id, fecha.strip(), hora.strip(), motivo.strip()),
            )
            return cur.lastrowid

    def actualizar_cita(self, cita_id: int, fecha: str, hora: str, motivo: str, estado: str, notas: str = ""):
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE citas SET fecha=?, hora=?, motivo=?, estado=?, notas_clinicas=? WHERE id=?",
                (fecha.strip(), hora.strip(), motivo.strip(), estado, notas.strip(), cita_id),
            )

    def obtener_detalle_cita(self, cita_id: int):
        with self.db.get_connection() as conn:
            cur = conn.execute(
                """
                SELECT ci.*, m.cliente_id, m.nombre AS mascota_nombre, m.especie, m.raza, m.edad, m.alergias, m.vacunas,
                       c.nombre AS dueno_nombre, c.telefono AS dueno_telefono, c.domicilio AS dueno_domicilio
                FROM citas ci
                JOIN mascotas m ON ci.mascota_id = m.id
                JOIN clientes c ON m.cliente_id = c.id
                WHERE ci.id = ?
                """,
                (cita_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def buscar_citas(self, filtro_texto: str = "", fecha_exacta: str = "", solo_atendidas: bool = False):
        with self.db.get_connection() as conn:
            sql = """
                SELECT ci.*, m.nombre AS mascota_nombre, m.especie, m.raza,
                       c.nombre AS dueno_nombre, c.telefono AS dueno_telefono
                FROM citas ci
                JOIN mascotas m ON ci.mascota_id = m.id
                JOIN clientes c ON m.cliente_id = c.id
                WHERE 1=1
            """
            params = []
            if solo_atendidas:
                sql += " AND ci.estado = 'Atendida'"
            if fecha_exacta:
                sql += " AND ci.fecha = ?"
                params.append(fecha_exacta.strip())
            if filtro_texto:
                q = f"%{filtro_texto.strip()}%"
                sql += " AND (m.nombre LIKE ? OR c.nombre LIKE ? OR ci.fecha LIKE ? OR ci.motivo LIKE ?)"
                params.extend([q, q, q, q])

            sql += " ORDER BY ci.fecha DESC, ci.hora ASC"
            cur = conn.execute(sql, params)
            return [dict(r) for r in cur.fetchall()]