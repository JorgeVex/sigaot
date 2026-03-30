"""
============================================================
SIGAOT - Modelo de Personal
Archivo: modelos/personal.py
Campos reales BD: fecha_nacimiento, tipo_sangre
============================================================
"""

from datetime import date
from base_datos.conexion import bd


class ModeloPersonal:
    """Gestión CRUD del personal de la empresa."""

    # ── Consultas ────────────────────────────────────────────

    @staticmethod
    def listar() -> list:
        """Devuelve todo el personal activo con su rol y fecha de registro."""
        sql = """
            SELECT p.id_personal, p.nombre_completo, p.numero_id,
                   p.telefono, p.correo, p.fecha_nacimiento,
                   p.tipo_sangre, p.ruta_imagen_cedula, p.id_rol,
                   r.nombre_rol, p.activo, p.fecha_registro
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

    # ── Lógica de cumpleaños (basada en fecha_nacimiento) ────

    @staticmethod
    def dias_para_cumpleanos(fecha_nacimiento) -> int | None:
        """
        Calcula los días que faltan para el próximo cumpleaños
        a partir de la fecha de nacimiento.
        Devuelve None si no hay fecha.
        """
        if fecha_nacimiento is None:
            return None
        hoy = date.today()
        try:
            proximo = date(hoy.year, fecha_nacimiento.month, fecha_nacimiento.day)
        except ValueError:
            # 29 de febrero en año no bisiesto → usar 28
            proximo = date(hoy.year, 2, 28)
        if proximo < hoy:
            try:
                proximo = date(hoy.year + 1, fecha_nacimiento.month, fecha_nacimiento.day)
            except ValueError:
                proximo = date(hoy.year + 1, 2, 28)
        return (proximo - hoy).days

    @staticmethod
    def hay_cumpleanos_proximos(dias_limite: int = 5) -> bool:
        """
        Devuelve True si algún empleado cumple años
        en los próximos `dias_limite` días.
        """
        todos = bd.consultar(
            "SELECT fecha_nacimiento FROM personal "
            "WHERE activo = 1 AND fecha_nacimiento IS NOT NULL"
        )
        for row in todos:
            dias = ModeloPersonal.dias_para_cumpleanos(row["fecha_nacimiento"])
            if dias is not None and 0 <= dias <= dias_limite:
                return True
        return False

    # ── Creación ─────────────────────────────────────────────

    @staticmethod
    def crear(nombre_completo: str, numero_id: str,
              telefono: str, correo: str, id_rol: int,
              ruta_imagen: str = None,
              fecha_nacimiento=None,
              tipo_sangre: str = None) -> int:
        """Inserta una persona nueva. Devuelve el id generado o -1."""
        sql = """
            INSERT INTO personal
                (nombre_completo, numero_id, telefono, correo,
                 fecha_nacimiento, tipo_sangre, id_rol, ruta_imagen_cedula)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        exito = bd.ejecutar(
            sql,
            (nombre_completo.strip(), numero_id.strip(),
             telefono.strip(), correo.strip(),
             fecha_nacimiento, tipo_sangre,
             id_rol, ruta_imagen),
        )
        return bd.ultima_id() if exito else -1

    # ── Actualización ────────────────────────────────────────

    @staticmethod
    def actualizar(id_personal: int, nombre_completo: str,
                   numero_id: str, telefono: str, correo: str,
                   id_rol: int, ruta_imagen: str = None,
                   fecha_nacimiento=None,
                   tipo_sangre: str = None) -> bool:
        """Actualiza los datos de una persona."""
        sql = """
            UPDATE personal
            SET    nombre_completo    = %s,
                   numero_id         = %s,
                   telefono          = %s,
                   correo            = %s,
                   fecha_nacimiento  = %s,
                   tipo_sangre       = %s,
                   id_rol            = %s,
                   ruta_imagen_cedula = %s
            WHERE  id_personal = %s
        """
        return bd.ejecutar(
            sql,
            (nombre_completo.strip(), numero_id.strip(),
             telefono.strip(), correo.strip(),
             fecha_nacimiento, tipo_sangre,
             id_rol, ruta_imagen, id_personal),
        )

    # ── Desactivación ────────────────────────────────────────

    @staticmethod
    def desactivar(id_personal: int) -> bool:
        sql = "UPDATE personal SET activo = 0 WHERE id_personal = %s"
        return bd.ejecutar(sql, (id_personal,))

    # ── Roles ────────────────────────────────────────────────

    @staticmethod
    def listar_roles() -> list:
        sql = "SELECT id_rol, nombre_rol FROM roles WHERE activo = 1"
        return bd.consultar(sql)
