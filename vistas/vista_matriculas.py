"""
============================================================
SIGAOT - Vista del Módulo de Matrículas
Archivo: vistas/vista_matriculas.py
============================================================
"""

from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QFrame, QScrollArea, QGridLayout,
    QSizePolicy, QSpacerItem,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from modelos.vehiculo  import ModeloVehiculo
from modelos.matricula import (
    ModeloMatricula, TIPOS_MATRICULA, ETIQUETAS_MATRICULA
)


# ── Paleta de colores por estado ─────────────────────────────
_COLORES_ESTADO = {
    "normal":      ("#FFFFFF", "#E0E3E8", "#1E2027"),   # fondo, borde, texto
    "proxima":     ("#EAF9F0", "#A8DFB5", "#1E5C2E"),
    "advertencia": ("#FFF8D6", "#F5C400", "#6B5200"),
    "urgente":     ("#FFE8CC", "#F5A623", "#7A4500"),
    "critica":     ("#FFDDDD", "#E74C3C", "#7A0000"),
    "vencida":     ("#F0D0D0", "#C0392B", "#5A0000"),
    "sin_fecha":   ("#F4F5F7", "#C0C4D0", "#6B7080"),
}

_ICONOS_ESTADO = {
    "normal":      "✅",
    "proxima":     "🟢",
    "advertencia": "🟡",
    "urgente":     "🟠",
    "critica":     "🔴",
    "vencida":     "❌",
    "sin_fecha":   "—",
}

_DESC_ESTADO = {
    "normal":      "Al día",
    "proxima":     "Próxima a vencer (1-2 meses)",
    "advertencia": "Vence en menos de 30 días",
    "urgente":     "Vence en menos de 15 días",
    "critica":     "¡Vence en menos de 7 días!",
    "vencida":     "VENCIDA",
    "sin_fecha":   "Sin fecha registrada",
}


class CardMatricula(QFrame):
    """
    Tarjeta individual que muestra el estado de una matrícula.
    El color de fondo cambia según los días restantes.
    """

    def __init__(self, tipo: str, fecha_vencimiento=None):
        super().__init__()
        self.tipo  = tipo
        self.fecha = fecha_vencimiento
        self._construir_ui()

    def _construir_ui(self):
        estado = ModeloMatricula.calcular_estado(self.fecha)
        fondo, borde, texto = _COLORES_ESTADO.get(
            estado, _COLORES_ESTADO["normal"]
        )

        self.setFixedSize(200, 120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {fondo};
                border: 2px solid {borde};
                border-radius: 10px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        # Icono + nombre
        fila_sup = QHBoxLayout()
        fila_sup.setSpacing(6)

        lbl_icono = QLabel(_ICONOS_ESTADO.get(estado, ""))
        lbl_icono.setFont(QFont("Arial", 16))
        fila_sup.addWidget(lbl_icono)

        lbl_nombre = QLabel(ETIQUETAS_MATRICULA.get(self.tipo, self.tipo))
        lbl_nombre.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_nombre.setStyleSheet(f"color: {texto};")
        fila_sup.addWidget(lbl_nombre, stretch=1)
        layout.addLayout(fila_sup)

        # "Vence" label
        lbl_vence_tit = QLabel("Vence")
        lbl_vence_tit.setStyleSheet("color: #6B7080; font-size: 11px;")
        layout.addWidget(lbl_vence_tit)

        # Fecha
        if self.fecha:
            if hasattr(self.fecha, "strftime"):
                fecha_str = self.fecha.strftime("%d-%m-%Y")
            else:
                # Convertir string YYYY-MM-DD → DD-MM-YYYY
                partes = str(self.fecha).split("-")
                fecha_str = f"{partes[2]}-{partes[1]}-{partes[0]}"
        else:
            fecha_str = "Sin fecha"

        lbl_fecha = QLabel(fecha_str)
        lbl_fecha.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_fecha.setStyleSheet(f"color: {texto};")
        layout.addWidget(lbl_fecha)

        # Días restantes
        if self.fecha and estado != "sin_fecha":
            hoy = date.today()
            if hasattr(self.fecha, "year"):
                dias = (self.fecha - hoy).days
            else:
                from datetime import datetime
                fv = datetime.strptime(str(self.fecha), "%Y-%m-%d").date()
                dias = (fv - hoy).days

            if dias < 0:
                desc_dias = f"Venció hace {abs(dias)} día(s)"
            elif dias == 0:
                desc_dias = "¡Vence hoy!"
            else:
                desc_dias = f"Faltan {dias} día(s)"
        else:
            desc_dias = _DESC_ESTADO.get(estado, "")

        lbl_dias = QLabel(desc_dias)
        lbl_dias.setStyleSheet(f"color: {texto}; font-size: 11px;")
        layout.addWidget(lbl_dias)


class VistaMatriculas(QWidget):
    """
    Módulo de Matrículas.
    - Panel izquierdo: lista de vehículos (solo placa).
    - Panel derecho: grid de tarjetas de matrículas.
    Emite `refrescar_badge` con True si hay vencimientos próximos.
    """

    refrescar_badge = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._id_vehiculo_actual = None
        self._construir_ui()

    # ── Construcción de UI ───────────────────────────────────

    def _construir_ui(self):
        layout_raiz = QVBoxLayout(self)
        layout_raiz.setContentsMargins(0, 0, 0, 0)
        layout_raiz.setSpacing(0)

        # Encabezado
        encabezado = QWidget()
        encabezado.setStyleSheet("background: transparent;")
        lyt_enc = QVBoxLayout(encabezado)
        lyt_enc.setContentsMargins(32, 28, 32, 12)
        lyt_enc.setSpacing(4)

        lbl_titulo = QLabel("Módulo Matrículas")
        lbl_titulo.setObjectName("titulo_modulo")
        lbl_titulo.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lyt_enc.addWidget(lbl_titulo)

        lbl_sub = QLabel("Selecciona un vehículo para ver sus matrículas")
        lbl_sub.setObjectName("subtitulo_modulo")
        lyt_enc.addWidget(lbl_sub)

        layout_raiz.addWidget(encabezado)

        # Cuerpo: lista + panel
        cuerpo = QWidget()
        cuerpo.setStyleSheet("background: transparent;")
        lyt_cuerpo = QHBoxLayout(cuerpo)
        lyt_cuerpo.setContentsMargins(32, 0, 32, 28)
        lyt_cuerpo.setSpacing(24)
        layout_raiz.addWidget(cuerpo, stretch=1)

        # ── Lista de vehículos ───────────────────────────────
        col_izq = QVBoxLayout()
        col_izq.setSpacing(8)

        lbl_lista = QLabel("Lista de vehículos")
        lbl_lista.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl_lista.setStyleSheet("color: #4A5060;")
        col_izq.addWidget(lbl_lista)

        self.lista_vehiculos = QListWidget()
        self.lista_vehiculos.setFixedWidth(200)
        self.lista_vehiculos.currentItemChanged.connect(
            self._al_seleccionar_vehiculo
        )
        col_izq.addWidget(self.lista_vehiculos, stretch=1)
        lyt_cuerpo.addLayout(col_izq)

        # ── Panel derecho ────────────────────────────────────
        col_der = QVBoxLayout()
        col_der.setSpacing(8)

        self.lbl_placa_actual = QLabel("Selecciona un vehículo")
        self.lbl_placa_actual.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_placa_actual.setStyleSheet("color: #1E2027;")
        col_der.addWidget(self.lbl_placa_actual)

        self.lbl_subtitulo_mat = QLabel("")
        self.lbl_subtitulo_mat.setStyleSheet("color: #6B7080; font-size: 12px;")
        col_der.addWidget(self.lbl_subtitulo_mat)

        # Scroll con grid de tarjetas
        self.scroll_mat = QScrollArea()
        self.scroll_mat.setWidgetResizable(True)
        self.scroll_mat.setFrameShape(QFrame.NoFrame)
        self.scroll_mat.setStyleSheet("background: transparent;")

        self.contenedor_cards = QWidget()
        self.contenedor_cards.setStyleSheet("background: transparent;")
        self.grid_cards = QGridLayout(self.contenedor_cards)
        self.grid_cards.setSpacing(16)
        self.grid_cards.setContentsMargins(0, 8, 0, 8)
        self.grid_cards.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self.scroll_mat.setWidget(self.contenedor_cards)
        col_der.addWidget(self.scroll_mat, stretch=1)

        # Leyenda de colores
        col_der.addWidget(self._crear_leyenda())

        lyt_cuerpo.addLayout(col_der, stretch=1)

    def _crear_leyenda(self) -> QWidget:
        """Crea la leyenda de colores en la parte inferior."""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        lyt = QHBoxLayout(widget)
        lyt.setContentsMargins(0, 4, 0, 0)
        lyt.setSpacing(16)

        leyenda = [
            ("#FFFFFF", "#E0E3E8", "Normal (> 60 días)"),
            ("#EAF9F0", "#A8DFB5", "Próxima (1-2 meses)"),
            ("#FFF8D6", "#F5C400", "Advertencia (< 30 días)"),
            ("#FFE8CC", "#F5A623", "Urgente (< 15 días)"),
            ("#FFDDDD", "#E74C3C", "Crítica (< 7 días)"),
            ("#F0D0D0", "#C0392B", "Vencida"),
        ]

        for fondo, borde, texto in leyenda:
            cuadro = QFrame()
            cuadro.setFixedSize(14, 14)
            cuadro.setStyleSheet(
                f"background: {fondo}; border: 2px solid {borde};"
                f"border-radius: 3px;"
            )
            lyt.addWidget(cuadro)

            lbl = QLabel(texto)
            lbl.setStyleSheet("color: #6B7080; font-size: 11px;")
            lyt.addWidget(lbl)

        lyt.addStretch()
        return widget

    # ── Lógica ───────────────────────────────────────────────

    def cargar_vehiculos(self):
        """Recarga la lista de vehículos habilitados."""
        self.lista_vehiculos.clear()
        vehiculos = ModeloVehiculo.listar_habilitados()
        for v in vehiculos:
            item = QListWidgetItem(v["placa"])
            item.setData(Qt.UserRole, v["id_vehiculo"])
            self.lista_vehiculos.addItem(item)

        # Verificar alertas globales
        hay_alertas = ModeloMatricula.hay_proximas_a_vencer(30)
        self.refrescar_badge.emit(hay_alertas)

    def _al_seleccionar_vehiculo(self, item: QListWidgetItem, _anterior):
        """Carga las tarjetas de matrículas del vehículo seleccionado."""
        if item is None:
            return

        id_vehiculo = item.data(Qt.UserRole)
        placa       = item.text()
        self._id_vehiculo_actual = id_vehiculo

        self.lbl_placa_actual.setText(f"Matrícula  {placa}")
        self.lbl_subtitulo_mat.setText(
            "Selecciona el tipo de matrícula que desees soportar"
        )

        self._mostrar_cards(id_vehiculo)

    def _mostrar_cards(self, id_vehiculo: int):
        """Limpia el grid y dibuja las tarjetas actualizadas."""
        # Limpiar cards anteriores
        while self.grid_cards.count():
            item = self.grid_cards.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Obtener matrículas de BD
        matriculas_bd = {
            m["tipo"]: m["fecha_vencimiento"]
            for m in ModeloMatricula.obtener_por_vehiculo(id_vehiculo)
        }

        # Dibujar una card por cada tipo
        columnas = 3
        for idx, tipo in enumerate(TIPOS_MATRICULA):
            fecha = matriculas_bd.get(tipo)
            card  = CardMatricula(tipo, fecha)
            fila  = idx // columnas
            col   = idx % columnas
            self.grid_cards.addWidget(card, fila, col)

        # Añadir strech al final
        self.grid_cards.setRowStretch(
            (len(TIPOS_MATRICULA) // columnas) + 1, 1
        )
