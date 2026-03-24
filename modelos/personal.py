"""
============================================================
SIGAOT - Modelo de Personal
Archivo: modelos/personal.py
Responsabilidad: acceso a datos de la tabla `personal`
============================================================
"""

from base_datos.conexion import bd


class ModeloPersonal:
    """Gestión CRUD del personal de la empresa."""

    # ── Consultas ────────────────────────────────────────────

    @staticmethod
    def listar() -> list:
        """Devuelve todo el personal activo con su rol."""
        sql = """
            SELECT p.id_personal, p.nombre_completo, p.numero_id,
                   p.telefono, p.correo, p.ruta_imagen_cedula,
                   p.id_rol, r.nombre_rol, p.activo, p.fecha_registro,
                   p.fecha_nacimiento, p.tipo_sangre
            FROM   personal p
            LEFT JOIN roles r ON r.id_rol = p.id_rol
            WHERE  p.activo = 1
            ORDER  BY p.nombre_completo
        """
        return bd.consultar(sql)

    @staticmethod
    def obtener_por_id(id_personal: int) -> dict | None:
        """Devuelve un registro de personal por su PK."""
        sql = "SELECT * FROM personal WHERE id_personal = %s"
        resultado = bd.consultar(sql, (id_personal,))
        return resultado[0] if resultado else None

    # ── Creación ─────────────────────────────────────────────

    @staticmethod
    def crear(nombre_completo: str, numero_id: str,
              telefono: str, correo: str,
              id_rol: int, ruta_imagen: str = None, fecha_nacimiento: str=None, tipo_sangre: str=None) -> int:
        """
        Inserta una persona nueva.
        Devuelve el id generado o -1 si falla.
        """
        sql = """
            INSERT INTO personal
                (nombre_completo, numero_id, telefono,
                 correo, id_rol, ruta_imagen_cedula, fecha_nacimiento, tipo_sangre)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        exito = bd.ejecutar(
            sql,
            (nombre_completo.strip(), numero_id.strip(),
             telefono.strip(), correo.strip(),
             id_rol, ruta_imagen, fecha_nacimiento, tipo_sangre),
        )
        return bd.ultima_id() if exito else -1

    # ── Actualización ────────────────────────────────────────

    @staticmethod
    def actualizar(id_personal: int, nombre_completo: str,
                   numero_id: str, telefono: str,
                   correo: str, id_rol: int,
                   ruta_imagen: str = None, fecha_nacimiento: str=None, tipo_sangre: str=None) -> bool:
        """Actualiza los datos de una persona."""
        sql = """
            UPDATE personal
            SET    nombre_completo    = %s,
                   numero_id         = %s,
                   telefono          = %s,
                   correo            = %s,
                   id_rol            = %s,
                   ruta_imagen_cedula = %s,
                   fecha_nacimiento = %s,
                   tipo_sangre = %s
            WHERE  id_personal = %s
        """
        return bd.ejecutar(
            sql,
            (nombre_completo.strip(), numero_id.strip(),
             telefono.strip(), correo.strip(),
             id_rol, ruta_imagen, id_personal),
        )

    # ── Desactivación ────────────────────────────────────────

    @staticmethod
    def desactivar(id_personal: int) -> bool:
        """Soft-delete de personal."""
        sql = "UPDATE personal SET activo = 0 WHERE id_personal = %s"
        return bd.ejecutar(sql, (id_personal,))

    # ── Roles ────────────────────────────────────────────────

    @staticmethod
    def listar_roles() -> list:
        """Devuelve todos los roles disponibles."""
        sql = "SELECT id_rol, nombre_rol FROM roles WHERE activo = 1"
        return bd.consultar(sql)
