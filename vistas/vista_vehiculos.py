"""
============================================================
SIGAOT - Vista del Módulo de Vehículos (v2)
Archivo: vistas/vista_vehiculos.py
Mejoras:
  - Botón de regreso en formulario y en lista
  - Al crear un vehículo se crean carpetas en disco
    C:/Users/Lenovo/Desktop/Vehiculos/<PLACA>/<MATRICULA>/
============================================================
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QLineEdit, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QScrollArea, QSizePolicy, QAbstractItemView,
    QFormLayout, QGroupBox, QInputDialog,
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from modelos.vehiculo  import ModeloVehiculo
from modelos.matricula import ModeloMatricula, TIPOS_MATRICULA, ETIQUETAS_MATRICULA

# ── Ruta raíz de carpetas de vehículos (igual que en matrículas) ──
RUTA_VEHICULOS = r"C:\Users\Lenovo\Desktop\Vehículos"


def crear_carpetas_vehiculo(placa: str) -> bool:
    """
    Crea la carpeta principal del vehículo y una subcarpeta
    por cada tipo de matrícula.
    Devuelve True si todo salió bien.
    """
    placa_limpia = placa.upper().strip()
    try:
        for tipo in TIPOS_MATRICULA:
            nombre_tipo = ETIQUETAS_MATRICULA[tipo].replace(" ", "_")
            ruta = os.path.join(RUTA_VEHICULOS, placa_limpia, nombre_tipo)
            os.makedirs(ruta, exist_ok=True)
        return True
    except OSError as e:
        print(f"[Carpetas] Error al crear carpetas para {placa}: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# Formulario registrar / editar vehículo
# ══════════════════════════════════════════════════════════════
class FormularioVehiculo(QWidget):
    """
    Formulario reutilizable para registrar y editar vehículos.
    Emite `guardado` o `cancelado` al terminar.
    """

    guardado  = pyqtSignal()
    cancelado = pyqtSignal()

    def __init__(self, id_vehiculo: int = None):
        super().__init__()
        self.id_vehiculo = id_vehiculo
        self._construir_ui()
        if id_vehiculo:
            self._cargar_datos(id_vehiculo)

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Encabezado con botón regreso ─────────────────────
        enc = QHBoxLayout()
        enc.setSpacing(14)
        enc.setContentsMargins(0, 0, 0, 0)

        btn_back = QPushButton("← Volver")
        btn_back.setObjectName("btn_secundario")
        btn_back.setFixedHeight(32)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.cancelado.emit)
        enc.addWidget(btn_back)

        titulo = "Registrar Vehículo" if not self.id_vehiculo else "Editar Vehículo"
        lbl = QLabel(titulo)
        lbl.setObjectName("titulo_modulo")
        lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        enc.addWidget(lbl, stretch=1)

        layout.addLayout(enc)
        layout.addSpacing(16)

        # ── Scroll ────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        contenido = QWidget()
        contenido.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(contenido)
        form_layout.setContentsMargins(0, 0, 20, 0)
        form_layout.setSpacing(14)

        estilo_grupo = """
            QGroupBox {
                font-weight: bold; font-size: 13px;
                border: 1.5px solid #E0E3E8;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 12px;
                background: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                color: #4A5060;
            }
        """

        # ── Datos del vehículo ───────────────────────────────
        grp_veh = QGroupBox("Datos del vehículo")
        grp_veh.setStyleSheet(estilo_grupo)
        g_lyt = QFormLayout(grp_veh)
        g_lyt.setContentsMargins(16, 20, 16, 16)
        g_lyt.setSpacing(12)
        g_lyt.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.inp_placa       = QLineEdit()
        self.inp_propietario = QLineEdit()
        self.inp_conductor   = QLineEdit()
        self.cbo_tipo        = QComboBox()
        self.cbo_tipo.addItems(["Camioneta", "Furgoneta"])

        for inp in [self.inp_placa, self.inp_propietario, self.inp_conductor]:
            inp.setFixedHeight(36)

        self.inp_placa.setPlaceholderText("Ej: WHX-426")
        self.inp_propietario.setPlaceholderText("Nombre del propietario")
        self.inp_conductor.setPlaceholderText("Nombre del conductor")

        g_lyt.addRow("Placa:", self.inp_placa)
        g_lyt.addRow("Propietario:", self.inp_propietario)
        g_lyt.addRow("Conductor:", self.inp_conductor)
        g_lyt.addRow("Tipo de vehículo:", self.cbo_tipo)
        form_layout.addWidget(grp_veh)

        # ── Vencimientos ─────────────────────────────────────
        grp_mat = QGroupBox("Vencimientos de matrículas")
        grp_mat.setStyleSheet(estilo_grupo)
        m_lyt = QFormLayout(grp_mat)
        m_lyt.setContentsMargins(16, 20, 16, 16)
        m_lyt.setSpacing(12)
        m_lyt.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.date_inputs = {}
        hoy = QDate.currentDate()

        for tipo in TIPOS_MATRICULA:
            de = QDateEdit()
            de.setCalendarPopup(True)
            de.setDate(hoy)
            de.setDisplayFormat("dd-MM-yyyy")
            de.setFixedHeight(36)
            de.setMinimumDate(QDate(2000, 1, 1))
            self.date_inputs[tipo] = de
            m_lyt.addRow(f"{ETIQUETAS_MATRICULA[tipo]}:", de)

        form_layout.addWidget(grp_mat)

        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setObjectName("lbl_error")
        self.lbl_mensaje.setWordWrap(True)
        form_layout.addWidget(self.lbl_mensaje)
        form_layout.addStretch()

        scroll.setWidget(contenido)
        layout.addWidget(scroll, stretch=1)
        layout.addSpacing(12)

        # ── Botones ───────────────────────────────────────────
        fila_btns = QHBoxLayout()
        fila_btns.setSpacing(12)
        fila_btns.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btn_secundario")
        btn_cancelar.setFixedHeight(38)
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.clicked.connect(self.cancelado.emit)
        fila_btns.addWidget(btn_cancelar)

        self.btn_guardar = QPushButton("Guardar ✓")
        self.btn_guardar.setObjectName("btn_primario")
        self.btn_guardar.setFixedHeight(38)
        self.btn_guardar.setMinimumWidth(130)
        self.btn_guardar.setCursor(Qt.PointingHandCursor)
        self.btn_guardar.clicked.connect(self._guardar)
        fila_btns.addWidget(self.btn_guardar)

        layout.addLayout(fila_btns)

    def _cargar_datos(self, id_vehiculo: int):
        veh = ModeloVehiculo.obtener_por_id(id_vehiculo)
        if not veh:
            return
        self.inp_placa.setText(veh["placa"])
        self.inp_placa.setReadOnly(True)
        self.inp_propietario.setText(veh["propietario"])
        self.inp_conductor.setText(veh["conductor"])
        idx = self.cbo_tipo.findText(veh["tipo_vehiculo"], Qt.MatchFixedString)
        if idx >= 0:
            self.cbo_tipo.setCurrentIndex(idx)

        for m in ModeloMatricula.obtener_por_vehiculo(id_vehiculo):
            tipo  = m["tipo"]
            fecha = m["fecha_vencimiento"]
            if tipo in self.date_inputs and fecha:
                if hasattr(fecha, "year"):
                    qd = QDate(fecha.year, fecha.month, fecha.day)
                else:
                    p  = str(fecha).split("-")
                    qd = QDate(int(p[0]), int(p[1]), int(p[2]))
                self.date_inputs[tipo].setDate(qd)

    def _guardar(self):
        placa       = self.inp_placa.text().strip().upper()
        propietario = self.inp_propietario.text().strip()
        conductor   = self.inp_conductor.text().strip()
        tipo_veh    = self.cbo_tipo.currentText()

        if not placa or not propietario or not conductor:
            self._msg_error("Por favor completa los campos obligatorios.")
            return

        es_nuevo = self.id_vehiculo is None

        if es_nuevo:
            if ModeloVehiculo.obtener_por_placa(placa):
                self._msg_error("Ya existe un vehículo con esa placa.")
                return
            id_veh = ModeloVehiculo.crear(placa, propietario, conductor, tipo_veh)
            if id_veh == -1:
                self._msg_error("Error al guardar en la base de datos.")
                return

            # Crear carpetas en disco
            ok_carpetas = crear_carpetas_vehiculo(placa)
            if not ok_carpetas:
                QMessageBox.warning(
                    self, "Aviso",
                    f"El vehículo se guardó en la BD, pero no se pudieron crear\n"
                    f"las carpetas en:\n{RUTA_VEHICULOS}\\{placa}\n\n"
                    f"Verifica que la ruta exista y tengas permisos de escritura."
                )
        else:
            id_veh = self.id_vehiculo
            ok = ModeloVehiculo.actualizar(
                id_veh, placa, propietario, conductor, tipo_veh
            )
            if not ok:
                self._msg_error("Error al actualizar el vehículo.")
                return

        # Guardar fechas de matrículas
        from datetime import date as _date
        fechas = {}
        for tipo, de in self.date_inputs.items():
            qd = de.date()
            fechas[tipo] = _date(qd.year(), qd.month(), qd.day())
        ModeloMatricula.guardar_todas(id_veh, fechas)

        self.lbl_mensaje.setObjectName("lbl_exito")
        self.lbl_mensaje.setText("✅ Vehículo guardado correctamente.")
        self.guardado.emit()

    def _msg_error(self, msg: str):
        self.lbl_mensaje.setObjectName("lbl_error")
        self.lbl_mensaje.setText(f"⚠ {msg}")


# ══════════════════════════════════════════════════════════════
# Tabla de vehículos
# ══════════════════════════════════════════════════════════════
class ListaVehiculos(QWidget):
    """Tabla con todos los vehículos y acciones por fila."""

    solicitar_editar      = pyqtSignal(int)
    solicitar_inhabilitar = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # ── Encabezado con regreso ────────────────────────────
        enc = QHBoxLayout()
        enc.setSpacing(14)

        btn_back = QPushButton("← Volver")
        btn_back.setObjectName("btn_secundario")
        btn_back.setFixedHeight(32)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self._ir_menu)
        enc.addWidget(btn_back)

        lbl = QLabel("Lista de vehículos registrados")
        lbl.setObjectName("titulo_modulo")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        enc.addWidget(lbl, stretch=1)

        layout.addLayout(enc)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "Placa", "Propietario", "Conductor",
            "Tipo", "Estado", "Acciones",
        ])
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setShowGrid(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet(
            "QTableWidget { alternate-background-color: #F9FAFC; }"
        )
        layout.addWidget(self.tabla)

    def actualizar(self):
        vehiculos = ModeloVehiculo.listar_todos()
        self.tabla.setRowCount(len(vehiculos))

        for fila, v in enumerate(vehiculos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(v["placa"]))
            self.tabla.setItem(fila, 1, QTableWidgetItem(v["propietario"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(v["conductor"]))
            self.tabla.setItem(fila, 3, QTableWidgetItem(v["tipo_vehiculo"]))

            estado = "Habilitado" if v["habilitado"] else "Inhabilitado"
            it_est = QTableWidgetItem(estado)
            it_est.setForeground(
                QColor("#27AE60") if v["habilitado"] else QColor("#E74C3C")
            )
            self.tabla.setItem(fila, 4, it_est)

            # Acciones
            w_acc = QWidget()
            lyt_a = QHBoxLayout(w_acc)
            lyt_a.setContentsMargins(4, 2, 4, 2)
            lyt_a.setSpacing(6)

            id_v  = v["id_vehiculo"]
            placa = v["placa"]

            btn_ed = QPushButton("Editar")
            btn_ed.setObjectName("btn_secundario")
            btn_ed.setFixedHeight(28)
            btn_ed.setCursor(Qt.PointingHandCursor)
            btn_ed.clicked.connect(lambda _, i=id_v: self.solicitar_editar.emit(i))
            lyt_a.addWidget(btn_ed)

            if v["habilitado"]:
                btn_inh = QPushButton("Inhabilitar")
                btn_inh.setObjectName("btn_peligro")
                btn_inh.setFixedHeight(28)
                btn_inh.setCursor(Qt.PointingHandCursor)
                btn_inh.clicked.connect(
                    lambda _, i=id_v, p=placa:
                    self.solicitar_inhabilitar.emit(i, p)
                )
                lyt_a.addWidget(btn_inh)
            else:
                btn_hab = QPushButton("Habilitar")
                btn_hab.setObjectName("btn_exito")
                btn_hab.setFixedHeight(28)
                btn_hab.setCursor(Qt.PointingHandCursor)
                btn_hab.clicked.connect(lambda _, i=id_v: self._habilitar(i))
                lyt_a.addWidget(btn_hab)

            self.tabla.setCellWidget(fila, 5, w_acc)
            self.tabla.setRowHeight(fila, 44)

    def _habilitar(self, id_vehiculo: int):
        if QMessageBox.question(
            self, "Confirmar",
            "¿Deseas habilitar este vehículo nuevamente?",
            QMessageBox.Yes | QMessageBox.No,
        ) == QMessageBox.Yes:
            ModeloVehiculo.habilitar(id_vehiculo)
            self.actualizar()

    def _ir_menu(self):
        """
        Sube la jerarquía de widgets hasta encontrar VistaVehiculos
        y navega a la página 0 (menú de opciones).
        """
        w = self.parent()
        while w is not None:
            if isinstance(w, VistaVehiculos):
                w.stack.setCurrentIndex(0)
                return
            w = w.parent()


# ══════════════════════════════════════════════════════════════
# Vista principal del módulo de Vehículos
# ══════════════════════════════════════════════════════════════
class VistaVehiculos(QWidget):
    """
    Módulo de gestión de vehículos.
    Sub-vistas: menú → formulario / lista → editar.
    """

    def __init__(self):
        super().__init__()
        self._construir_ui()

    def _construir_ui(self):
        self.layout_raiz = QVBoxLayout(self)
        self.layout_raiz.setContentsMargins(32, 28, 32, 28)
        self.layout_raiz.setSpacing(0)

        # Encabezado
        enc = QHBoxLayout()
        enc.setSpacing(14)

        btn_back = QPushButton("← Inicio")
        btn_back.setObjectName("btn_secundario")
        btn_back.setFixedHeight(32)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self._ir_inicio)
        enc.addWidget(btn_back)

        col_enc = QVBoxLayout()
        lbl_mod = QLabel("Módulo de gestión de vehículos")
        lbl_mod.setObjectName("titulo_modulo")
        lbl_mod.setFont(QFont("Segoe UI", 20, QFont.Bold))
        col_enc.addWidget(lbl_mod)

        lbl_sub = QLabel("Opciones  ·  Selecciona la acción que desees realizar")
        lbl_sub.setObjectName("subtitulo_modulo")
        col_enc.addWidget(lbl_sub)

        enc.addLayout(col_enc, stretch=1)
        self.layout_raiz.addLayout(enc)
        self.layout_raiz.addSpacing(16)

        # Stack interno
        self.stack = QStackedWidget()
        self.layout_raiz.addWidget(self.stack, stretch=1)

        # Página 0: menú
        self.stack.addWidget(self._crear_pagina_menu())

        # Página 1: formulario nuevo
        self.form_registrar = FormularioVehiculo()
        self.form_registrar.guardado.connect(self._tras_guardar)
        self.form_registrar.cancelado.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.form_registrar)

        # Página 2: lista
        self.lista_veh = ListaVehiculos()
        self.lista_veh.solicitar_editar.connect(self._abrir_editar)
        self.lista_veh.solicitar_inhabilitar.connect(self._inhabilitar)
        self.stack.addWidget(self.lista_veh)

        # Página 3: formulario editar (placeholder, se reemplaza)
        self._idx_editar = 3
        self.stack.addWidget(QWidget())

    def _crear_pagina_menu(self) -> QWidget:
        pagina = QWidget()
        pagina.setStyleSheet("background: transparent;")
        lyt = QVBoxLayout(pagina)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(16)

        opciones = [
            ("🚗", "Registrar y editar vehículos",
             "Registra placa, propietario, conductor, tipo de vehículo\n"
             "y fechas de vencimiento de matrículas.",
             [("Registrar", self._abrir_registrar),
              ("Ver lista",  self._ir_lista)]),

            ("🔍", "Verificación de matrículas",
             "Visualiza las matrículas asociadas a los vehículos\n"
             "con alertas de vencimiento en tiempo real.",
             [("Verificar", self._ir_matriculas)]),

            ("🚫", "Vehículos inhabilitados",
             "Consulta los vehículos fuera de servicio y reactívalos\n"
             "cuando sea necesario.",
             [("Visualizar", self._ir_lista)]),
        ]

        for icono, titulo, desc, btns in opciones:
            lyt.addWidget(self._card_opcion(icono, titulo, desc, btns))

        lyt.addStretch()
        return pagina

    @staticmethod
    def _card_opcion(icono, titulo, desc, botones) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background-color: #FFFFFF;
                border: 1.5px solid #E0E3E8;
                border-radius: 10px;
            }
            QFrame#card:hover { border-color: #F5C400; }
        """)
        lyt = QHBoxLayout(card)
        lyt.setContentsMargins(20, 16, 20, 16)
        lyt.setSpacing(16)

        lbl_ico = QLabel(icono)
        lbl_ico.setFont(QFont("Arial", 36))
        lbl_ico.setFixedSize(64, 64)
        lbl_ico.setAlignment(Qt.AlignCenter)
        lbl_ico.setStyleSheet("background: #FFFBEA; border-radius: 32px;")
        lyt.addWidget(lbl_ico)

        col = QVBoxLayout()
        col.setSpacing(4)

        lbl_t = QLabel(titulo)
        lbl_t.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_t.setStyleSheet("color: #1E2027;")
        col.addWidget(lbl_t)

        lbl_d = QLabel(desc)
        lbl_d.setStyleSheet("color: #6B7080; font-size: 12px;")
        lbl_d.setWordWrap(True)
        col.addWidget(lbl_d)

        fila_b = QHBoxLayout()
        fila_b.setSpacing(8)
        for texto, accion in botones:
            b = QPushButton(texto)
            b.setObjectName("btn_secundario")
            b.setFixedHeight(32)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(accion)
            fila_b.addWidget(b)
        fila_b.addStretch()
        col.addLayout(fila_b)

        lyt.addLayout(col, stretch=1)
        return card

    # ── Navegación interna ───────────────────────────────────

    def _abrir_registrar(self):
        self.stack.removeWidget(self.form_registrar)
        self.form_registrar.deleteLater()
        self.form_registrar = FormularioVehiculo()
        self.form_registrar.guardado.connect(self._tras_guardar)
        self.form_registrar.cancelado.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.insertWidget(1, self.form_registrar)
        self.stack.setCurrentIndex(1)

    def _ir_lista(self):
        self.lista_veh.actualizar()
        self.stack.setCurrentIndex(2)

    def _ir_matriculas(self):
        ventana = self.window()
        if hasattr(ventana, "_navegar"):
            ventana._navegar(2)

    def _ir_inicio(self):
        ventana = self.window()
        if hasattr(ventana, "_navegar"):
            ventana._navegar(0)

    def _abrir_editar(self, id_vehiculo: int):
        form = FormularioVehiculo(id_vehiculo=id_vehiculo)
        form.guardado.connect(self._tras_guardar_edicion)
        form.cancelado.connect(lambda: self.stack.setCurrentIndex(2))
        w = self.stack.widget(self._idx_editar)
        if w:
            self.stack.removeWidget(w)
            w.deleteLater()
        self.stack.insertWidget(self._idx_editar, form)
        self.stack.setCurrentIndex(self._idx_editar)

    def _tras_guardar(self):
        self.stack.setCurrentIndex(0)

    def _tras_guardar_edicion(self):
        self.lista_veh.actualizar()
        self.stack.setCurrentIndex(2)

    def _inhabilitar(self, id_vehiculo: int, placa: str):
        motivo, ok = QInputDialog.getText(
            self, "Inhabilitar vehículo",
            f"¿Motivo para inhabilitar {placa}? (opcional):",
        )
        if ok:
            ModeloVehiculo.inhabilitar(id_vehiculo, motivo)
            self.lista_veh.actualizar()

    def cargar_lista(self):
        """Llamado desde la ventana principal."""
        pass
