"""
============================================================
SIGAOT - Punto de entrada de la aplicación
Archivo: main.py

Uso:
    python main.py

Requisitos:
    pip install PyQt5 mysql-connector-python

Asegúrate de:
    1. Tener MySQL corriendo con la BD importada desde
       SQL/sigaot_bd.sql
    2. Ajustar usuario/contraseña en base_datos/conexion.py
    3. Colocar las imágenes en recursos/IMG/
       - logo.png  (logo circular de Trans-Alcayá)
       - user.png  (icono de usuario genérico)
============================================================
"""

import sys
import os

# ── Asegurar que el directorio raíz del proyecto esté en sys.path ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

from base_datos.conexion import bd
from vistas.vista_login  import VistaLogin
from controladores.controlador_login import ControladorLogin


def cargar_estilos(app: QApplication) -> None:
    """Lee el archivo QSS y lo aplica a toda la aplicación."""
    ruta_qss = os.path.join(BASE_DIR, "recursos", "estilos", "estilo.qss")
    if os.path.exists(ruta_qss):  
        with open(ruta_qss, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"[Estilos] No se encontró el archivo QSS en: {ruta_qss}")


def configurar_app(app: QApplication) -> None:
    """Aplica configuraciones globales a la aplicación Qt."""
    app.setApplicationName("SIGAOT")
    app.setOrganizationName("Trans-Alcayá")
    app.setApplicationVersion("1.0.0")

    # Fuente base
    fuente = QFont("Segoe UI", 10)
    app.setFont(fuente)

    # Icono de la aplicación (ventanas y taskbar)
    ruta_icono = os.path.join(BASE_DIR, "recursos", "IMG", "logo.png")
    if os.path.exists(ruta_icono):
        app.setWindowIcon(QIcon(ruta_icono))

    # Escala automática en pantallas HiDPI
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def verificar_conexion_bd() -> bool:
    """
    Intenta conectar a la base de datos.
    Devuelve True si logra conectar, False en caso contrario.
    """
    ok = bd.conectar()
    if not ok:
        QMessageBox.critical(
            None,
            "Error de conexión",
            "No se pudo conectar a la base de datos MySQL.\n\n"
            "Por favor verifica:\n"
            "  • Que el servidor MySQL esté corriendo.\n"
            "  • Que las credenciales en base_datos/conexion.py sean correctas.\n"
            "  • Que la base de datos 'sigaot' exista.\n\n"
            "La aplicación se cerrará.",
        )
    return ok


def main() -> None:
    """Función principal: arranca la aplicación SIGAOT."""
    app = QApplication(sys.argv)
    configurar_app(app)
    cargar_estilos(app)

    # Verificar conexión a BD antes de mostrar nada
    if not verificar_conexion_bd():
        sys.exit(1)

    # Mostrar pantalla de login
    vista_login = VistaLogin()
    # El controlador conecta señales y maneja el flujo
    ctrl_login  = ControladorLogin(vista_login, app)   # noqa: F841

    vista_login.show()

    # Código de salida
    codigo = app.exec_()

    # Cerrar conexión BD al salir
    bd.desconectar()
    sys.exit(codigo)


if __name__ == "__main__":
    main()
