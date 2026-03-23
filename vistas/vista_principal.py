"""
============================================================
SIGAOT - Ventana principal (shell con sidebar) v2
Archivo: vistas/vista_principal.py
Cambios:
  - Agrega módulo Personal al sidebar (índice 3)
  - Sidebar con 4 ítems de navegación
============================================================
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy, QStackedWidget,
    QSpacerItem,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon

from vistas.vista_inicio     import VistaInicio
from vistas.vista_vehiculos  import VistaVehiculos
from vistas.vista_matriculas import VistaMatriculas
from vistas.vista_personal   import VistaPersonal


class VentanaPrincipal(QMainWindow):
    """
    Ventana principal de SIGAOT.
    Sidebar de navegación + QStackedWidget con los módulos.
    """

    def __init__(self, datos_usuario: dict):
        super().__init__()
        self.datos_usuario = datos_usuario
        self._alerta_activa = False
        self._construir_ui()
        self._navegar(0)

    # ── Construcción de la UI ────────────────────────────────

    def _construir_ui(self):
        self.setWindowTitle("SIGAOT – Trans-Alcayá")
        self.setMinimumSize(980, 640)
        self.resize(1140, 700)

        central = QWidget()
        self.setCentralWidget(central)

        layout_raiz = QHBoxLayout(central)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        # Sidebar
        self.sidebar = self._crear_sidebar()
        layout_raiz.addWidget(self.sidebar)

        # Área de contenido
        self.stack = QStackedWidget()
        self.stack.setObjectName("contenido")
        layout_raiz.addWidget(self.stack, stretch=1)

        # Módulos
        self.vista_inicio     = VistaInicio(self.datos_usuario)
        self.vista_vehiculos  = VistaVehiculos()
        self.vista_matriculas = VistaMatriculas()
        self.vista_personal   = VistaPersonal()

        self.stack.addWidget(self.vista_inicio)      # 0
        self.stack.addWidget(self.vista_vehiculos)   # 1
        self.stack.addWidget(self.vista_matriculas)  # 2
        self.stack.addWidget(self.vista_personal)    # 3

        # Badge de alerta de matrículas
        self.vista_matriculas.refrescar_badge.connect(
            self._actualizar_badge_alerta
        )

    def _crear_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(0)

        # Logo
        contenedor_logo = QWidget()
        lyt_logo = QVBoxLayout(contenedor_logo)
        lyt_logo.setContentsMargins(0, 0, 0, 4)
        lyt_logo.setAlignment(Qt.AlignCenter)

        lbl_logo = QLabel()
        lbl_logo.setObjectName("lbl_logo_sidebar")
        lbl_logo.setAlignment(Qt.AlignCenter)
        ruta = os.path.join(
            os.path.dirname(__file__), "..", "recursos", "IMG", "logo.png"
        )
        if os.path.exists(ruta):
            pix = QPixmap(ruta).scaled(
                80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            lbl_logo.setPixmap(pix)
        else:
            lbl_logo.setText("🚚")
            lbl_logo.setFont(QFont("Arial", 36))
        lyt_logo.addWidget(lbl_logo)
        layout.addWidget(contenedor_logo)

        # Bienvenido
        lbl_bienvenido = QLabel("Bienvenido")
        lbl_bienvenido.setObjectName("lbl_bienvenido")
        layout.addWidget(lbl_bienvenido)

        lbl_usuario = QLabel(self.datos_usuario.get("usuario", "Usuario"))
        lbl_usuario.setObjectName("lbl_usuario_sidebar")
        layout.addWidget(lbl_usuario)

        sep = QFrame()
        sep.setObjectName("separador_sidebar")
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        layout.addSpacing(8)

        # Botones de navegación
        self.btns_nav = []

        self._btn_inicio = self._crear_btn_nav("  🏠  Inicio", 0)
        layout.addWidget(self._btn_inicio)

        self._btn_vehiculos = self._crear_btn_nav("  🚗  Vehículos", 1)
        layout.addWidget(self._btn_vehiculos)

        # Matrículas + badge
        contenedor_mat = QWidget()
        lyt_mat = QHBoxLayout(contenedor_mat)
        lyt_mat.setContentsMargins(0, 0, 8, 0)
        lyt_mat.setSpacing(0)

        self._btn_matriculas = self._crear_btn_nav("  📋  Matrículas", 2)
        lyt_mat.addWidget(self._btn_matriculas, stretch=1)

        self._badge = QLabel("!")
        self._badge.setObjectName("badge_alerta")
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setFixedSize(18, 18)
        self._badge.setVisible(False)
        self._badge.setStyleSheet("""
            background-color: #E74C3C; color: white; border-radius: 9px;
            font-size: 10px; font-weight: bold;
        """)
        lyt_mat.addWidget(self._badge)
        layout.addWidget(contenedor_mat)

        # Personal
        self._btn_personal = self._crear_btn_nav("  👥  Personal", 3)
        layout.addWidget(self._btn_personal)

        # Espacio y cerrar sesión
        layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        btn_salir = QPushButton("  🚪  Cerrar sesión")
        btn_salir.setCursor(Qt.PointingHandCursor)
        btn_salir.setStyleSheet("""
            background-color: transparent; color: #A0A4B0;
            border: none; text-align: left; padding: 10px 16px;
            font-size: 13px; margin: 2px 8px; border-radius: 6px;
        """)
        btn_salir.clicked.connect(self.close)
        layout.addWidget(btn_salir)

        return sidebar

    def _crear_btn_nav(self, texto: str, indice: int) -> QPushButton:
        btn = QPushButton(texto)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("activo", False)
        self.btns_nav.append((btn, indice))
        btn.clicked.connect(lambda _, i=indice: self._navegar(i))
        return btn

    # ── Navegación ───────────────────────────────────────────

    def _navegar(self, indice: int):
        self.stack.setCurrentIndex(indice)
        for btn, idx in self.btns_nav:
            btn.setProperty("activo", idx == indice)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if indice == 2:
            self.vista_matriculas.cargar_vehiculos()
        if indice == 1:
            self.vista_vehiculos.cargar_lista()

    # ── Badge ────────────────────────────────────────────────

    def _actualizar_badge_alerta(self, visible: bool):
        self._alerta_activa = visible
        self._badge.setVisible(visible)

    def activar_alerta_matriculas(self):
        self._badge.setVisible(True)
