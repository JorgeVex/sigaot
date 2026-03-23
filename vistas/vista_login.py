"""
============================================================
SIGAOT - Vista de Login
Archivo: vistas/vista_login.py
============================================================
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy,
    QSpacerItem,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QIcon


class VistaLogin(QWidget):
    """
    Pantalla de inicio de sesión.
    Emite la señal `login_exitoso` cuando las credenciales
    son válidas; el controlador se encarga de la lógica.
    """

    # Señal que el controlador conecta
    intentar_login = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self._construir_ui()

    # ── Construcción de la interfaz ──────────────────────────

    def _construir_ui(self):
        """Monta todos los widgets de la pantalla de login."""
        self.setWindowTitle("SIGAOT – Iniciar sesión")
        self.setFixedSize(420, 540)
        self.setObjectName("ventana_login")

        # Fondo gris oscuro igual que el sidebar
        self.setStyleSheet("background-color: #FFFFFF;")

        # Layout raíz con padding
        raiz = QVBoxLayout(self)
        raiz.setAlignment(Qt.AlignCenter)
        raiz.setContentsMargins(40, 30, 40, 30)
        raiz.setSpacing(0)

        # ── Panel blanco central ────────────────────────────
        panel = QFrame()
        panel.setObjectName("panel_login")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout_panel = QVBoxLayout(panel)
        layout_panel.setContentsMargins(36, 36, 36, 36)
        layout_panel.setSpacing(14)
        layout_panel.setAlignment(Qt.AlignTop)

        # Logo de la empresa
        lbl_logo = QLabel()
        lbl_logo.setAlignment(Qt.AlignCenter)
        ruta_logo = os.path.join(
            os.path.dirname(__file__), "..", "recursos", "IMG", "logo.png"
        )
        if os.path.exists(ruta_logo):
            pix = QPixmap(ruta_logo).scaled(
                110, 110,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            lbl_logo.setPixmap(pix)
        else:
            lbl_logo.setText("🚚")
            lbl_logo.setFont(QFont("Arial", 48))
        layout_panel.addWidget(lbl_logo)

        # Título
        lbl_titulo = QLabel("SIGAOT")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #1E2027; letter-spacing: 2px;")
        layout_panel.addWidget(lbl_titulo)

        # Subtítulo
        lbl_sub = QLabel("Trans-Alcayá")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet("color: #6B7080; font-size: 13px;")
        layout_panel.addWidget(lbl_sub)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #E0E3E8; margin: 8px 0;")
        layout_panel.addWidget(sep)

        # Campo: Usuario
        lbl_usuario = QLabel("Usuario")
        lbl_usuario.setObjectName("lbl_campo")
        layout_panel.addWidget(lbl_usuario)

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Ingresa tu usuario")
        self.input_usuario.setFixedHeight(38)
        layout_panel.addWidget(self.input_usuario)

        # Campo: Contraseña
        lbl_pw = QLabel("Contraseña")
        lbl_pw.setObjectName("lbl_campo")
        layout_panel.addWidget(lbl_pw)

        self.input_pw = QLineEdit()
        self.input_pw.setPlaceholderText("Ingresa tu contraseña")
        self.input_pw.setEchoMode(QLineEdit.Password)
        self.input_pw.setFixedHeight(38)
        layout_panel.addWidget(self.input_pw)

        # Mensaje de error
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("lbl_error")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setWordWrap(True)
        layout_panel.addWidget(self.lbl_error)

        # Botón Ingresar
        self.btn_ingresar = QPushButton("Ingresar →")
        self.btn_ingresar.setObjectName("btn_primario")
        self.btn_ingresar.setFixedHeight(42)
        self.btn_ingresar.setCursor(Qt.PointingHandCursor)
        self.btn_ingresar.setFont(QFont("Segoe UI", 13, QFont.Bold))
        layout_panel.addWidget(self.btn_ingresar)

        raiz.addWidget(panel)

        # Pie de página
        lbl_pie = QLabel("© 2025 Trans-Alcayá – Todos los derechos reservados")
        lbl_pie.setAlignment(Qt.AlignCenter)
        lbl_pie.setStyleSheet("color: #5A5E6A; font-size: 11px; margin-top: 16px;")
        raiz.addWidget(lbl_pie)

        # ── Conexiones internas ─────────────────────────────
        self.btn_ingresar.clicked.connect(self._emitir_login)
        self.input_pw.returnPressed.connect(self._emitir_login)
        self.input_usuario.returnPressed.connect(self.input_pw.setFocus)

    # ── Métodos públicos ─────────────────────────────────────

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error debajo del formulario."""
        self.lbl_error.setText(mensaje)

    def limpiar(self):
        """Resetea el formulario."""
        self.input_usuario.clear()
        self.input_pw.clear()
        self.lbl_error.clear()
        self.input_usuario.setFocus()

    # ── Slots privados ───────────────────────────────────────

    def _emitir_login(self):
        """Emite la señal con usuario y contraseña."""
        self.lbl_error.clear()
        usuario = self.input_usuario.text().strip()
        contrasena = self.input_pw.text()

        if not usuario or not contrasena:
            self.mostrar_error("Por favor completa todos los campos.")
            return

        self.intentar_login.emit(usuario, contrasena)
