"""
============================================================
SIGAOT - Módulo de conexión a la base de datos MySQL
Archivo: base_datos/conexion.py
Patrón: Singleton para reutilizar la conexión
============================================================
"""

import mysql.connector
from mysql.connector import Error
import hashlib


# ── Configuración de conexión ────────────────────────────────
_CONFIG_BD = {
    "host":     "127.0.0.1",
    "port":     3306,
    "user":     "root",          # Cambiar según tu instalación
    "password": "100101*",          # Cambiar según tu instalación
    "database": "sigaot",
    "charset":  "utf8mb4",
    "use_pure": True,
}


class ConexionBD:
    """
    Clase Singleton que gestiona la conexión única a MySQL.
    Se reutiliza durante toda la sesión de la aplicación.
    """

    _instancia = None          # Instancia Singleton
    _conexion  = None          # Objeto de conexión activo

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
        return cls._instancia

    # ── Conexión / desconexión ───────────────────────────────

    def conectar(self) -> bool:
        """
        Establece la conexión con la base de datos.
        Devuelve True si tiene éxito, False en caso contrario.
        """
        try:
            if self._conexion and self._conexion.is_connected():
                return True                     # Ya estamos conectados

            self._conexion = mysql.connector.connect(**_CONFIG_BD)
            print("[BD] Conexión establecida correctamente.")
            return True

        except Error as err:
            print(f"[BD] Error al conectar: {err}")
            self._conexion = None
            return False

    def desconectar(self) -> None:
        """Cierra la conexión si está abierta."""
        if self._conexion and self._conexion.is_connected():
            self._conexion.close()
            print("[BD] Conexión cerrada.")

    # ── Cursor / consultas ───────────────────────────────────

    def obtener_cursor(self, diccionario: bool = False):
        """
        Devuelve un cursor activo.
        Si la conexión se perdió, intenta reconectar.
        """
        try:
            if not self._conexion or not self._conexion.is_connected():
                self.conectar()
            return self._conexion.cursor(dictionary=diccionario)
        except Error as err:
            print(f"[BD] Error al obtener cursor: {err}")
            return None

    def ejecutar(self, sql: str, params: tuple = None,
                 confirmar: bool = True) -> bool:
        """
        Ejecuta una sentencia DML (INSERT, UPDATE, DELETE).
        Devuelve True si tuvo éxito.
        """
        cursor = self.obtener_cursor()
        if cursor is None:
            return False
        try:
            cursor.execute(sql, params)
            if confirmar:
                self._conexion.commit()
            return True
        except Error as err:
            print(f"[BD] Error en ejecutar: {err}")
            self._conexion.rollback()
            return False
        finally:
            cursor.close()

    def consultar(self, sql: str, params: tuple = None,
                  diccionario: bool = True) -> list:
        """
        Ejecuta una sentencia SELECT y devuelve los resultados
        como lista de diccionarios (por defecto).
        """
        cursor = self.obtener_cursor(diccionario=diccionario)
        if cursor is None:
            return []
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Error as err:
            print(f"[BD] Error en consultar: {err}")
            return []
        finally:
            cursor.close()

    def ultima_id(self) -> int:
        """Devuelve el último id insertado en la sesión actual."""
        cursor = self.obtener_cursor()
        if cursor is None:
            return -1
        try:
            cursor.execute("SELECT LAST_INSERT_ID()")
            fila = cursor.fetchone()
            return fila[0] if fila else -1
        finally:
            cursor.close()


# ── Instancia global ─────────────────────────────────────────
bd = ConexionBD()


# ── Utilidad de hash ─────────────────────────────────────────

def hashear_contrasena(texto: str) -> str:
    """Devuelve el hash SHA-256 (hex) de la cadena recibida."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()
