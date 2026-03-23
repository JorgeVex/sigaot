"""
============================================================
SIGAOT - Modelo de Usuarios
Archivo: modelos/usuario.py
Responsabilidad: acceso a datos de la tabla `usuarios`
============================================================
"""

from base_datos.conexion import bd, hashear_contrasena


class ModeloUsuario:
    """Gestión CRUD de usuarios del sistema."""

    # ── Autenticación ────────────────────────────────────────

    @staticmethod
    def autenticar(usuario: str, contrasena: str) -> dict | None:
        """
        Verifica credenciales.
        Devuelve el registro del usuario o None si falla.
        """
        sql = """
            SELECT u.id_usuario, u.usuario, u.id_rol,
                   r.nombre_rol, u.id_personal
            FROM   usuarios u
            JOIN   roles r ON r.id_rol = u.id_rol
            WHERE  u.usuario   = %s
              AND  u.contrasena = %s
              AND  u.activo    = 1
        """
        hash_pw = hashear_contrasena(contrasena)
        resultado = bd.consultar(sql, (usuario, hash_pw))

        if resultado:
            # Actualizar último acceso
            bd.ejecutar(
                "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id_usuario = %s",
                (resultado[0]["id_usuario"],),
            )
            return resultado[0]
        return None

    # ── Listado ──────────────────────────────────────────────

    @staticmethod
    def listar() -> list:
        """Devuelve todos los usuarios activos con su rol."""
        sql = """
            SELECT u.id_usuario, u.usuario, r.nombre_rol,
                   p.nombre_completo, u.activo
            FROM   usuarios u
            JOIN   roles r ON r.id_rol = u.id_rol
            LEFT JOIN personal p ON p.id_personal = u.id_personal
            WHERE  u.activo = 1
            ORDER  BY u.usuario
        """
        return bd.consultar(sql)

    # ── Creación ─────────────────────────────────────────────

    @staticmethod
    def crear(usuario: str, contrasena: str,
              id_rol: int, id_personal: int = None) -> bool:
        """Inserta un nuevo usuario en el sistema."""
        sql = """
            INSERT INTO usuarios (usuario, contrasena, id_rol, id_personal)
            VALUES (%s, %s, %s, %s)
        """
        hash_pw = hashear_contrasena(contrasena)
        return bd.ejecutar(sql, (usuario, hash_pw, id_rol, id_personal))

    # ── Actualización ────────────────────────────────────────

    @staticmethod
    def actualizar_contrasena(id_usuario: int, nueva: str) -> bool:
        """Cambia la contraseña de un usuario."""
        sql = "UPDATE usuarios SET contrasena = %s WHERE id_usuario = %s"
        return bd.ejecutar(sql, (hashear_contrasena(nueva), id_usuario))

    # ── Desactivación ────────────────────────────────────────

    @staticmethod
    def desactivar(id_usuario: int) -> bool:
        """Desactiva (soft delete) un usuario."""
        sql = "UPDATE usuarios SET activo = 0 WHERE id_usuario = %s"
        return bd.ejecutar(sql, (id_usuario,))
