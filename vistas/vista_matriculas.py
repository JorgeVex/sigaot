"""
============================================================
SIGAOT - Vista del Módulo de Matrículas (v2)
Archivo: vistas/vista_matriculas.py
Mejoras:
  - Cards responsivos (FlowLayout propio)
  - Sin líneas/bordes internos dentro de cada card
  - Botón "Soportar matrícula" con subida de imagen
  - Crea carpetas por placa y tipo de matrícula automáticamente
  - Botón de regreso
============================================================
"""

import os
import shutil
from datetime import date, datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QFrame, QScrollArea, QSizePolicy,
    QPushButton, QFileDialog, QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect
from PyQt5.QtGui import QFont

from modelos.vehiculo  import ModeloVehiculo
from modelos.matricula import (
    ModeloMatricula, TIPOS_MATRICULA, ETIQUETAS_MATRICULA
)

# ── Ruta raíz de carpetas de vehículos ───────────────────────
RUTA_VEHICULOS = r"C:\Users\Lenovo\Desktop\Vehículos"

# ── Paleta: (fondo, acento, texto-título, texto-sub) ─────────
_PALETA = {
    "normal":      ("#FFFFFF", "#C8CDD8", "#1E2027", "#6B7080"),
    "proxima":     ("#F0FBF4", "#3DBE6A", "#1A5C35", "#3A8050"),
    "advertencia": ("#FFFBEA", "#E6B800", "#5C4400", "#8A6800"),
    "urgente":     ("#FFF3E0", "#F07820", "#6B3200", "#A05000"),
    "critica":     ("#FFF0F0", "#D93025", "#6B0000", "#A01010"),
    "vencida":     ("#FAE8E8", "#B02010", "#5A0000", "#901010"),
    "sin_fecha":   ("#F4F5F7", "#B0B4C0", "#6B7080", "#9099A8"),
}

_CHIP_TEXTO = {
    "normal":      "Al día",
    "proxima":     "Próxima",
    "advertencia": "< 30 días",
    "urgente":     "< 15 días",
    "critica":     "< 7 días  ⚠",
    "vencida":     "VENCIDA",
    "sin_fecha":   "Sin fecha",
}


# ══════════════════════════════════════════════════════════════
# FlowLayout – filas adaptativas al ancho del contenedor
# ══════════════════════════════════════════════════════════════
class FlowLayout(QWidget):
    """
    Widget contenedor que distribuye sus hijos en filas
    que se adaptan automáticamente al ancho disponible.
    """

    def __init__(self, espaciado: int = 16, parent=None):
        super().__init__(parent)
        self._espaciado = espaciado
        self._items: list[QWidget] = []
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def agregar(self, widget: QWidget):
        widget.setParent(self)
        widget.show()
        self._items.append(widget)
        self._reorganizar()

    def limpiar(self):
        for w in self._items:
            w.hide()
            w.setParent(None)
            w.deleteLater()
        self._items.clear()
        self.setMinimumHeight(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reorganizar()

    def _reorganizar(self):
        if not self._items:
            self.setMinimumHeight(40)
            return

        ancho = self.width()
        if ancho <= 0:
            return

        esp = self._espaciado
        x, y = 0, 0
        alto_fila = 0

        for w in self._items:
            sw = w.sizeHint().width()
            sh = w.sizeHint().height()
            if sw <= 0:
                sw = 260
            if sh <= 0:
                sh = 165

            if x + sw > ancho and x > 0:
                x = 0
                y += alto_fila + esp
                alto_fila = 0

            w.setGeometry(QRect(x, y, sw, sh))
            x += sw + esp
            alto_fila = max(alto_fila, sh)

        total_alto = y + alto_fila + esp
        self.setMinimumHeight(total_alto)


# ══════════════════════════════════════════════════════════════
# Card individual de matrícula
# ══════════════════════════════════════════════════════════════
class CardMatricula(QFrame):
    """
    Tarjeta que muestra estado de una matrícula.
    Sin líneas internas; borde-izquierdo de color como acento.
    """

    def __init__(self, tipo: str, fecha_vencimiento=None,
                 placa: str = "", id_vehiculo: int = 0):
        super().__init__()
        self.tipo        = tipo
        self.fecha       = fecha_vencimiento
        self.placa       = placa
        self.id_vehiculo = id_vehiculo
        self._construir_ui()

    def sizeHint(self) -> QSize:
        return QSize(255, 162)

    def _construir_ui(self):
        estado = ModeloMatricula.calcular_estado(self.fecha)
        fondo, acento, txt_tit, txt_sub = _PALETA.get(estado, _PALETA["normal"])

        # Frame: fondo + borde izquierdo de acento, SIN bordes internos
        self.setStyleSheet(f"""
            CardMatricula {{
                background-color: {fondo};
                border-radius: 12px;
                border: none;
                border-left: 5px solid {acento};
            }}
            QLabel {{
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }}
            QPushButton {{
                /* el botón tiene su propio estilo inline */
            }}
        """)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 13, 13, 12)
        layout.setSpacing(0)

        # ── Fila superior ─────────────────────────────────────
        fila_sup = QHBoxLayout()
        fila_sup.setSpacing(8)
        fila_sup.setContentsMargins(0, 0, 0, 0)

        lbl_nombre = QLabel(ETIQUETAS_MATRICULA.get(self.tipo, self.tipo))
        lbl_nombre.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_nombre.setStyleSheet(f"color: {txt_tit};")
        fila_sup.addWidget(lbl_nombre, stretch=1)

        chip = QLabel(_CHIP_TEXTO.get(estado, ""))
        chip.setFont(QFont("Segoe UI", 8, QFont.Bold))
        chip.setStyleSheet(f"""
            color: {acento};
            border: 1.5px solid {acento};
            border-radius: 7px;
            padding: 1px 7px;
            background: transparent;
        """)
        chip.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        fila_sup.addWidget(chip)

        layout.addLayout(fila_sup)
        layout.addSpacing(8)

        # ── Fecha ─────────────────────────────────────────────
        if self.fecha:
            if hasattr(self.fecha, "strftime"):
                fecha_str = self.fecha.strftime("%d-%m-%Y")
            else:
                p = str(self.fecha).split("-")
                fecha_str = f"{p[2]}-{p[1]}-{p[0]}"
        else:
            fecha_str = "—"

        lbl_vence = QLabel("Vence")
        lbl_vence.setStyleSheet(f"color: {txt_sub}; font-size: 10px;")
        layout.addWidget(lbl_vence)

        lbl_fecha = QLabel(fecha_str)
        lbl_fecha.setFont(QFont("Segoe UI", 16, QFont.Bold))
        lbl_fecha.setStyleSheet(f"color: {txt_tit};")
        layout.addWidget(lbl_fecha)

        # ── Días restantes ────────────────────────────────────
        desc = ""
        if self.fecha and estado != "sin_fecha":
            hoy = date.today()
            if hasattr(self.fecha, "year"):
                dias = (self.fecha - hoy).days
            else:
                fv   = datetime.strptime(str(self.fecha), "%Y-%m-%d").date()
                dias = (fv - hoy).days

            if dias < 0:
                desc = f"Venció hace {abs(dias)} día(s)"
            elif dias == 0:
                desc = "¡Vence hoy!"
            else:
                desc = f"Faltan {dias} día(s)"

        lbl_dias = QLabel(desc)
        lbl_dias.setStyleSheet(f"color: {txt_sub}; font-size: 11px;")
        layout.addWidget(lbl_dias)

        layout.addSpacing(8)

        # ── Botón soportar ────────────────────────────────────
        btn_sop = QPushButton("📎  Soportar matrícula")
        btn_sop.setCursor(Qt.PointingHandCursor)
        btn_sop.setFixedHeight(28)
        btn_sop.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {acento};
                border: 1.5px solid {acento};
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 10px;
            }}
            QPushButton:hover {{
                background-color: {acento}28;
            }}
            QPushButton:pressed {{
                background-color: {acento}50;
            }}
        """)
        btn_sop.clicked.connect(self._subir_soporte)
        layout.addWidget(btn_sop)

    # ── Subir soporte ────────────────────────────────────────

    def _subir_soporte(self):
        """
        Copia imagen/PDF a la carpeta de la matrícula y,
        de forma OBLIGATORIA, solicita la nueva fecha de
        vencimiento antes de completar la operación.
        """
        if not self.placa:
            QMessageBox.warning(self, "Sin vehículo",
                                "No hay vehículo asociado.")
            return

        ruta_archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar comprobante o matrícula renovada",
            "",
            "Imágenes y PDF (*.png *.jpg *.jpeg *.pdf *.bmp *.tiff)",
        )
        if not ruta_archivo:
            return

        # ── Modal OBLIGATORIO: nueva fecha de vencimiento ────
        from vistas.dialogo_fecha import DialogoNuevaFecha
        dialogo = DialogoNuevaFecha(
            tipo=ETIQUETAS_MATRICULA.get(self.tipo, self.tipo),
            placa=self.placa,
            parent=self,
        )
        if dialogo.exec_() != dialogo.Accepted:
            QMessageBox.information(
                self, "Operación cancelada",
                "Debes ingresar la nueva fecha de vencimiento\n"
                "para poder guardar el soporte."
            )
            return

        nueva_fecha = dialogo.obtener_fecha()

        # ── Copiar archivo ───────────────────────────────────
        nombre_tipo     = ETIQUETAS_MATRICULA.get(
            self.tipo, self.tipo
        ).replace(" ", "_")
        carpeta_destino = os.path.join(
            RUTA_VEHICULOS, self.placa, nombre_tipo
        )
        try:
            os.makedirs(carpeta_destino, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(
                self, "Error de carpeta",
                f"No se pudo crear:\n{carpeta_destino}\n\n{e}"
            )
            return

        marca   = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext     = os.path.splitext(ruta_archivo)[1]
        destino = os.path.join(
            carpeta_destino, f"{nombre_tipo}_{marca}{ext}"
        )
        try:
            shutil.copy2(ruta_archivo, destino)
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar archivo", str(e))
            return

        # ── Actualizar fecha en BD ───────────────────────────
        ok = ModeloMatricula.guardar(self.id_vehiculo, self.tipo, nueva_fecha)
        if ok:
            QMessageBox.information(
                self, "✅ Soporte registrado",
                f"Comprobante guardado en:\n{destino}\n\n"
                f"Nueva fecha de vencimiento:\n"
                f"{nueva_fecha.strftime('%d-%m-%Y')}"
            )
            vista = self._buscar_vista_matriculas()
            if vista:
                vista._mostrar_cards(self.id_vehiculo, self.placa)
        else:
            QMessageBox.warning(
                self, "Atención",
                "Archivo guardado, pero no se pudo actualizar\n"
                "la fecha en la base de datos."
            )

    def _buscar_vista_matriculas(self):
        """Sube la jerarquía hasta encontrar VistaMatriculas."""
        from vistas.vista_matriculas import VistaMatriculas
        w = self.parent()
        while w:
            if isinstance(w, VistaMatriculas):
                return w
            w = w.parent()
        return None


# ══════════════════════════════════════════════════════════════
# Vista principal del módulo
# ══════════════════════════════════════════════════════════════
class VistaMatriculas(QWidget):
    """
    Módulo de Matrículas con cards responsivos y soporte
    de archivos por vehículo.
    """

    refrescar_badge = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._id_vehiculo_actual = None
        self._placa_actual       = ""
        self._construir_ui()

    def _construir_ui(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 0)
        raiz.setSpacing(0)

        # ── Encabezado ────────────────────────────────────────
        encabezado = QWidget()
        encabezado.setStyleSheet("background: transparent;")
        lyt_enc = QHBoxLayout(encabezado)
        lyt_enc.setContentsMargins(32, 22, 32, 8)
        lyt_enc.setSpacing(14)

        btn_back = QPushButton("← Inicio")
        btn_back.setObjectName("btn_secundario")
        btn_back.setFixedHeight(32)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self._ir_inicio)
        lyt_enc.addWidget(btn_back)

        col_tit = QVBoxLayout()
        col_tit.setSpacing(2)

        lbl_titulo = QLabel("Módulo Matrículas")
        lbl_titulo.setObjectName("titulo_modulo")
        lbl_titulo.setFont(QFont("Segoe UI", 20, QFont.Bold))
        col_tit.addWidget(lbl_titulo)

        lbl_sub = QLabel("Selecciona un vehículo para ver sus matrículas")
        lbl_sub.setObjectName("subtitulo_modulo")
        col_tit.addWidget(lbl_sub)

        lyt_enc.addLayout(col_tit, stretch=1)
        raiz.addWidget(encabezado)

        # ── Cuerpo: lista + cards ─────────────────────────────
        cuerpo = QWidget()
        cuerpo.setStyleSheet("background: transparent;")
        lyt_cuerpo = QHBoxLayout(cuerpo)
        lyt_cuerpo.setContentsMargins(32, 0, 32, 24)
        lyt_cuerpo.setSpacing(24)
        raiz.addWidget(cuerpo, stretch=1)

        # Lista de vehículos
        col_izq = QVBoxLayout()
        col_izq.setSpacing(8)

        lbl_lista = QLabel("Vehículos")
        lbl_lista.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_lista.setStyleSheet("color: #4A5060;")
        col_izq.addWidget(lbl_lista)

        self.lista_vehiculos = QListWidget()
        self.lista_vehiculos.setFixedWidth(180)
        self.lista_vehiculos.currentItemChanged.connect(
            self._al_seleccionar_vehiculo
        )
        col_izq.addWidget(self.lista_vehiculos, stretch=1)
        lyt_cuerpo.addLayout(col_izq)

        # Panel derecho
        col_der = QVBoxLayout()
        col_der.setSpacing(6)

        self.lbl_placa_actual = QLabel("Selecciona un vehículo")
        self.lbl_placa_actual.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.lbl_placa_actual.setStyleSheet("color: #1E2027;")
        col_der.addWidget(self.lbl_placa_actual)

        self.lbl_subtitulo_mat = QLabel("")
        self.lbl_subtitulo_mat.setStyleSheet("color: #6B7080; font-size: 12px;")
        col_der.addWidget(self.lbl_subtitulo_mat)

        # ScrollArea con FlowLayout
        self.scroll_mat = QScrollArea()
        self.scroll_mat.setWidgetResizable(True)
        self.scroll_mat.setFrameShape(QFrame.NoFrame)
        self.scroll_mat.setStyleSheet("background: transparent; border: none;")

        self.flow_container = QWidget()
        self.flow_container.setStyleSheet("background: transparent;")
        self.flow_layout = FlowLayout(espaciado=16)

        vbox_flow = QVBoxLayout(self.flow_container)
        vbox_flow.setContentsMargins(0, 4, 4, 4)
        vbox_flow.setSpacing(0)
        vbox_flow.addWidget(self.flow_layout)
        vbox_flow.addStretch()

        self.scroll_mat.setWidget(self.flow_container)
        col_der.addWidget(self.scroll_mat, stretch=1)

        col_der.addWidget(self._crear_leyenda())
        lyt_cuerpo.addLayout(col_der, stretch=1)

    def _crear_leyenda(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lyt = QHBoxLayout(w)
        lyt.setContentsMargins(0, 4, 0, 0)
        lyt.setSpacing(12)

        items = [
            ("#C8CDD8", "Normal"),
            ("#3DBE6A", "Próxima"),
            ("#E6B800", "< 30 días"),
            ("#F07820", "< 15 días"),
            ("#D93025", "< 7 días"),
            ("#B02010", "Vencida"),
        ]
        for color, label in items:
            barra = QFrame()
            barra.setFixedSize(4, 16)
            barra.setStyleSheet(
                f"background: {color}; border-radius: 2px; border: none;"
            )
            lyt.addWidget(barra)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #6B7080; font-size: 11px;")
            lyt.addWidget(lbl)

        lyt.addStretch()
        return w

    # ── Lógica ───────────────────────────────────────────────

    def cargar_vehiculos(self):
        self.lista_vehiculos.clear()
        for v in ModeloVehiculo.listar_habilitados():
            item = QListWidgetItem(v["placa"])
            item.setData(Qt.UserRole,     v["id_vehiculo"])
            item.setData(Qt.UserRole + 1, v["placa"])
            self.lista_vehiculos.addItem(item)

        hay_alertas = ModeloMatricula.hay_proximas_a_vencer(30)
        self.refrescar_badge.emit(hay_alertas)

        # Mantener selección anterior
        if self._placa_actual:
            for i in range(self.lista_vehiculos.count()):
                if self.lista_vehiculos.item(i).text() == self._placa_actual:
                    self.lista_vehiculos.setCurrentRow(i)
                    break

    def _al_seleccionar_vehiculo(self, item, _anterior):
        if item is None:
            return
        self._id_vehiculo_actual = item.data(Qt.UserRole)
        self._placa_actual       = item.text()
        self.lbl_placa_actual.setText(f"Matrícula  {self._placa_actual}")
        self.lbl_subtitulo_mat.setText(
            "Selecciona el tipo de matrícula que desees soportar"
        )
        self._mostrar_cards(self._id_vehiculo_actual, self._placa_actual)

    def _mostrar_cards(self, id_vehiculo: int, placa: str):
        self.flow_layout.limpiar()
        matriculas_bd = {
            m["tipo"]: m["fecha_vencimiento"]
            for m in ModeloMatricula.obtener_por_vehiculo(id_vehiculo)
        }
        for tipo in TIPOS_MATRICULA:
            card = CardMatricula(
                tipo,
                matriculas_bd.get(tipo),
                placa=placa,
                id_vehiculo=id_vehiculo,
            )
            self.flow_layout.agregar(card)

    def _ir_inicio(self):
        ventana = self.window()
        if hasattr(ventana, "_navegar"):
            ventana._navegar(0)
