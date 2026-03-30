"""
============================================================
SIGAOT - Vista de Inicio
Archivo: vistas/vista_inicio.py
============================================================
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QSizePolicy, QSpacerItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont


class VistaInicio(QWidget):
    """
    Pantalla de bienvenida que se muestra al iniciar sesión.
    Muestra el logo, nombre del sistema y una descripción.
    """

    def __init__(self, datos_usuario: dict):
        super().__init__()
        self.datos_usuario = datos_usuario
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Título del sistema
        lbl_titulo = QLabel("¡Bienvenido a SIGAOT!")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setObjectName("titulo_modulo")
        lbl_titulo.setFont(QFont("Segoe UI", 26, QFont.Bold))
        layout.addWidget(lbl_titulo)

        layout.addSpacing(12)

        # Subtítulo
        lbl_sub = QLabel(
            "Sistema Integrado de Gestión Administrativa y Operativa de Transporte"
        )
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setFont(QFont("Segoe UI", 14))
        lbl_sub.setStyleSheet("color: #4A5060;")
        lbl_sub.setWordWrap(True)
        layout.addWidget(lbl_sub)

        layout.addSpacing(32)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #E0E3E8;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        layout.addSpacing(32)

        # Descripción
        lbl_desc = QLabel(
            "Tu solución completa para optimizar y controlar todas las operaciones\n"
            "de tu empresa de transporte. Gestiona de manera eficiente tu flota,\n"
            "rutas, conductores y servicios desde una sola plataforma."
        )
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setStyleSheet("color: #6B7080; font-size: 14px; line-height: 1.6;")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        layout.addSpacing(40)

        # ── Tarjetas de módulos ──────────────────────────────
        fila_cards = QHBoxLayout()
        fila_cards.setSpacing(20)
        fila_cards.setAlignment(Qt.AlignCenter)

        cards_info = [
            ("🚗", "Vehículos",
             "Registra, edita e inhabilita\nlos vehículos de la flota."),
            ("📋", "Matrículas",
             "Controla fechas de vencimiento\ny recibe alertas a tiempo."),
            ("👥", "Personal",
             "Administra el equipo,\nroles y accesos del sistema."),
        ]

        for icono, titulo, desc in cards_info:
            card = self._crear_card(icono, titulo, desc)
            fila_cards.addWidget(card)

        layout.addLayout(fila_cards)

        # Empuje + logo en esquina inferior derecha
        layout.addStretch(1)

        fila_pie = QHBoxLayout()
        fila_pie.addStretch(1)

        contenedor_logo = QVBoxLayout()
        contenedor_logo.setAlignment(Qt.AlignBottom | Qt.AlignRight)

        lbl_logo = QLabel()
        ruta = os.path.join(
            os.path.dirname(__file__), "..", "recursos", "IMG", "Transalcaya.png"
        )
        if os.path.exists(ruta):
            pix = QPixmap(ruta).scaled(
                120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            lbl_logo.setPixmap(pix)
        else:
            lbl_logo.setText("🚚")
            lbl_logo.setFont(QFont("Arial", 48))

        lbl_logo.setAlignment(Qt.AlignRight)
        contenedor_logo.addWidget(lbl_logo)

        fila_pie.addLayout(contenedor_logo)
        layout.addLayout(fila_pie)

    @staticmethod
    def _crear_card(icono: str, titulo: str, desc: str) -> QFrame:
        """Crea una mini tarjeta de módulo para la pantalla de inicio."""
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(200)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        card.setStyleSheet("""
            QFrame#card {
                background-color: #FFFFFF;
                border: 1.5px solid #E0E3E8;
                border-radius: 12px;
                padding: 16px;
            }
            QFrame#card:hover {
                border-color: #F5C400;
            }
        """)

        lyt = QVBoxLayout(card)
        lyt.setAlignment(Qt.AlignTop)
        lyt.setSpacing(8)

        lbl_icono = QLabel(icono)
        lbl_icono.setFont(QFont("Arial", 32))
        lbl_icono.setAlignment(Qt.AlignCenter)
        lyt.addWidget(lbl_icono)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("color: #1E2027;")
        lyt.addWidget(lbl_titulo)

        lbl_desc = QLabel(desc)
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("color: #6B7080; font-size: 12px;")
        lyt.addWidget(lbl_desc)

        return card
