"""
============================================================
SIGAOT - Controlador de Login
Archivo: controladores/controlador_login.py
Responsabilidad: coordina la vista de login con el modelo
                 de usuarios y lanza la ventana principal.
============================================================
"""

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QObject

from modelos.usuario   import ModeloUsuario
from modelos.matricula import ModeloMatricula


class ControladorLogin(QObject):
    """
    Controlador MVC para la pantalla de inicio de sesión.
    Recibe las señales de la vista, consulta el modelo y
    decide qué hacer a continuación.
    """

    def __init__(self, vista_login, app):
        super().__init__()
        self.vista   = vista_login
        self.app     = app        # Referencia a QApplication (para estilos)
        self._ventana_principal = None

        # Conectar señal de la vista → slot del controlador
        self.vista.intentar_login.connect(self._procesar_login)

    # ── Slots ────────────────────────────────────────────────

    def _procesar_login(self, usuario: str, contrasena: str):
        """
        Valida credenciales contra la base de datos.
        Si son correctas, abre la ventana principal.
        """
        datos = ModeloUsuario.autenticar(usuario, contrasena)

        if datos is None:
            self.vista.mostrar_error(
                "Usuario o contraseña incorrectos. Intenta de nuevo."
            )
            return

        # ── Login exitoso ────────────────────────────────────
        self.vista.hide()

        # Importar aquí para evitar ciclos
        from vistas.vista_principal import VentanaPrincipal
        from controladores.controlador_principal import ControladorPrincipal

        self._ventana_principal = VentanaPrincipal(datos)
        self._ctrl_principal    = ControladorPrincipal(
            self._ventana_principal, datos
        )
        self._ventana_principal.show()

        # Verificar alertas de matrículas al iniciar
        self._verificar_alertas_inicio()

    def _verificar_alertas_inicio(self):
        """
        Comprueba si hay matrículas próximas a vencer
        y muestra una notificación de escritorio.
        """
        hay_alertas = ModeloMatricula.hay_proximas_a_vencer(30)
        if hay_alertas:
            # Activar badge en el sidebar
            self._ventana_principal.activar_alerta_matriculas()

            # Notificación emergente (QMessageBox no bloqueante)
            msg = QMessageBox(self._ventana_principal)
            msg.setWindowTitle("⚠ Alerta de matrículas")
            msg.setIcon(QMessageBox.Warning)
            msg.setText(
                "🔔 Hay matrículas con fecha próxima de vencimiento.\n\n"
                "Por favor revisa el módulo de Matrículas para más detalles."
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #FFFFFF;
                    font-size: 13px;
                }
                QPushButton {
                    background-color: #F5C400;
                    color: #1E2027;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 20px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #D4A900; }
            """)
            msg.exec_()
