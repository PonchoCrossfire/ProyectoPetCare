from datetime import datetime
from database import DatabaseManager

class PetCareService:
    # --- RF-06: AUTENTICACIÓN Y ROLES ---
    @staticmethod
    def autenticar(username: str, password: str):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT idUsuario, username, nombreCompleto, rol 
                FROM usuario 
                WHERE username = ? AND password = ?
            """, (username.strip(), password.strip()))
            row = cursor.fetchone()
            return dict(row) if row else None

    # --- RF-02: CLIENTES ---
    @staticmethod
    def crear_cliente(nombre: str, paterno: str, materno: str) -> int:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cliente (nombreCliente, aPaterno, aMaterno, fechaRegistro)
                VALUES (?, ?, ?, ?)
            """, (nombre.strip(), paterno.strip(), materno.strip() if materno else None, fecha))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def listar_clientes():
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT idCliente, nombreCliente, aPaterno, aMaterno, fechaRegistro FROM cliente ORDER BY idCliente DESC")
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def actualizar_cliente(id_cliente: int, nombre: str, paterno: str, materno: str):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cliente 
                SET nombreCliente = ?, aPaterno = ?, aMaterno = ?
                WHERE idCliente = ?
            """, (nombre.strip(), paterno.strip(), materno.strip() if materno else None, int(id_cliente)))
            conn.commit()

    @staticmethod
    def eliminar_cliente(id_cliente: int):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cliente WHERE idCliente = ?", (int(id_cliente),))
            conn.commit()

    # --- RF-03: MASCOTAS ---
    @staticmethod
    def crear_mascota(nombre: str, especie: str, raza: str, edad: int, id_cliente: int) -> int:
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mascota (nombreMascota, especie, raza, edad, idCliente)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre.strip(), especie.strip(), raza.strip(), int(edad), int(id_cliente)))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def listar_mascotas_por_cliente(id_cliente: int):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT idMascota, nombreMascota, especie, raza, edad FROM mascota WHERE idCliente = ?", (int(id_cliente),))
            return [dict(row) for row in cursor.fetchall()]

    # --- RF-05: HISTORIAL CLÍNICO DE MASCOTA ---
    @staticmethod
    def buscar_mascotas_por_nombre(nombre_mascota: str):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            sql = """
                SELECT 
                    m.idMascota,
                    m.nombreMascota,
                    m.especie,
                    m.raza,
                    m.edad,
                    (cl.nombreCliente || ' ' || cl.aPaterno || ' ' || COALESCE(cl.aMaterno, '')) AS nomDueno
                FROM mascota m
                JOIN cliente cl ON m.idCliente = cl.idCliente
                WHERE m.nombreMascota LIKE ?
                ORDER BY m.nombreMascota ASC
            """
            cursor.execute(sql, (f"%{nombre_mascota.strip()}%",))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def obtener_historial_citas_mascota(id_mascota: int):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            sql = """
                SELECT 
                    c.idCita,
                    c.fechaCita,
                    c.horaCita,
                    (cl.nombreCliente || ' ' || cl.aPaterno || ' ' || COALESCE(cl.aMaterno, '')) AS nomDueno
                FROM cita c
                JOIN cliente cl ON c.idCliente = cl.idCliente
                WHERE c.idMascota = ?
                ORDER BY c.fechaCita DESC, c.horaCita DESC
            """
            cursor.execute(sql, (int(id_mascota),))
            return [dict(row) for row in cursor.fetchall()]

    # --- RF-01 / RF-07: CITAS Y AGENDA ---
    @staticmethod
    def crear_cita(fecha: str, hora: str, id_mascota: int, id_cliente: int) -> int:
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cita (fechaCita, horaCita, idMascota, idCliente)
                VALUES (?, ?, ?, ?)
            """, (fecha.strip(), hora.strip(), int(id_mascota), int(id_cliente)))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def actualizar_cita(id_cita: int, fecha: str, hora: str):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cita 
                SET fechaCita = ?, horaCita = ?
                WHERE idCita = ?
            """, (fecha.strip(), hora.strip(), int(id_cita)))
            conn.commit()

    @staticmethod
    def eliminar_cita(id_cita: int):
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cita WHERE idCita = ?", (int(id_cita),))
            conn.commit()

    @staticmethod
    def buscar_agenda(filtro_dueno="", filtro_mascota="", filtro_fecha=""):
        sql = """
            SELECT 
                c.idCita,
                c.fechaCita,
                c.horaCita,
                (cl.nombreCliente || ' ' || cl.aPaterno || ' ' || COALESCE(cl.aMaterno, '')) AS nomDueno,
                m.nombreMascota,
                m.especie,
                m.raza
            FROM cita c
            JOIN cliente cl ON c.idCliente = cl.idCliente
            JOIN mascota m ON c.idMascota = m.idMascota
            WHERE 1=1
        """
        params = []
        if filtro_dueno:
            sql += " AND (cl.nombreCliente LIKE ? OR cl.aPaterno LIKE ?)"
            params.extend([f"%{filtro_dueno}%", f"%{filtro_dueno}%"])
        if filtro_mascota:
            sql += " AND m.nombreMascota LIKE ?"
            params.append(f"%{filtro_mascota}%")
        if filtro_fecha:
            sql += " AND c.fechaCita LIKE ?"
            params.append(f"%{filtro_fecha}%")

        sql += " ORDER BY c.fechaCita ASC, c.horaCita ASC"

        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def obtener_citas_por_fecha(fecha_str: str):
        sql = """
            SELECT 
                c.idCita,
                c.fechaCita,
                c.horaCita,
                (cl.nombreCliente || ' ' || cl.aPaterno || ' ' || COALESCE(cl.aMaterno, '')) AS nomDueno,
                m.nombreMascota,
                m.especie,
                m.raza
            FROM cita c
            JOIN cliente cl ON c.idCliente = cl.idCliente
            JOIN mascota m ON c.idMascota = m.idMascota
            WHERE c.fechaCita = ?
            ORDER BY c.horaCita ASC
        """
        with DatabaseManager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (fecha_str.strip(),))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def obtener_metricas():
        with DatabaseManager.get_connection() as conn:
            cur = conn.cursor()
            total_clientes = cur.execute("SELECT COUNT(*) FROM cliente").fetchone()[0]
            total_mascotas = cur.execute("SELECT COUNT(*) FROM mascota").fetchone()[0]
            total_citas = cur.execute("SELECT COUNT(*) FROM cita").fetchone()[0]
            return total_clientes, total_mascotas, total_citas