"""
============================================================
SIGAOT - Vista del Módulo de Vehículos
Archivo: vistas/vista_vehiculos.py
============================================================
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QLineEdit, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QScrollArea, QSizePolicy, QSpacerItem, QAbstractItemView,
    QFormLayout, QGroupBox,
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from modelos.vehiculo  import ModeloVehiculo
from modelos.matricula import ModeloMatricula, TIPOS_MATRICULA, ETIQUETAS_MATRICULA


# ══════════════════════════════════════════════════════════════
# Sub-vista: Formulario para registrar / editar vehículo
# ══════════════════════════════════════════════════════════════

class FormularioVehiculo(QWidget):
    """
    Formulario reutilizable para registrar y editar vehículos.
    Emite `guardado` al completar con éxito.
    """

    guardado  = pyqtSignal()
    cancelado = pyqtSignal()

    def __init__(self, id_vehiculo: int = None):
        super().__init__()
        self.id_vehiculo = id_vehiculo     # None → nuevo vehículo
        self._construir_ui()
        if id_vehiculo:
            self._cargar_datos(id_vehiculo)

    # ── UI ───────────────────────────────────────────────────

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Encabezado
        titulo = "Registrar Vehículo" if not self.id_vehiculo else "Editar Vehículo"
        lbl = QLabel(titulo)
        lbl.setObjectName("titulo_modulo")
        lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        layout.addWidget(lbl)

        layout.addSpacing(20)

        # Scroll para el formulario
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        contenido = QWidget()
        contenido.setStyleSheet("background: transparent;")
        form_layout = QVBoxLayout(contenido)
        form_layout.setContentsMargins(0, 0, 20, 0)
        form_layout.setSpacing(14)

        # ── Datos del vehículo ───────────────────────────────
        grupo_veh = QGroupBox("Datos del vehículo")
        grupo_veh.setStyleSheet("""
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
        """)
        g_layout = QFormLayout(grupo_veh)
        g_layout.setContentsMargins(16, 20, 16, 16)
        g_layout.setSpacing(12)
        g_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.inp_placa       = QLineEdit()
        self.inp_propietario = QLineEdit()
        self.inp_conductor   = QLineEdit()
        self.cbo_tipo        = QComboBox()
        self.cbo_tipo.addItems(["Camioneta", "Furgoneta"])

        for inp in [self.inp_placa, self.inp_propietario,
                    self.inp_conductor]:
            inp.setFixedHeight(36)

        self.inp_placa.setPlaceholderText("Ej: WHX-426")
        self.inp_propietario.setPlaceholderText("Nombre del propietario")
        self.inp_conductor.setPlaceholderText("Nombre del conductor")

        g_layout.addRow("Placa:", self.inp_placa)
        g_layout.addRow("Propietario:", self.inp_propietario)
        g_layout.addRow("Conductor:", self.inp_conductor)
        g_layout.addRow("Tipo de vehículo:", self.cbo_tipo)
        form_layout.addWidget(grupo_veh)

        # ── Vencimientos de matrículas ───────────────────────
        grupo_mat = QGroupBox("Vencimientos de matrículas")
        grupo_mat.setStyleSheet(grupo_veh.styleSheet())
        m_layout = QFormLayout(grupo_mat)
        m_layout.setContentsMargins(16, 20, 16, 16)
        m_layout.setSpacing(12)
        m_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.date_inputs = {}
        hoy = QDate.currentDate()

        for tipo in TIPOS_MATRICULA:
            etiqueta = ETIQUETAS_MATRICULA[tipo]
            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDate(hoy)
            date_edit.setDisplayFormat("dd-MM-yyyy")
            date_edit.setFixedHeight(36)
            date_edit.setSpecialValueText("Sin fecha")
            date_edit.setMinimumDate(QDate(2000, 1, 1))
            self.date_inputs[tipo] = date_edit
            m_layout.addRow(f"{etiqueta}:", date_edit)

        form_layout.addWidget(grupo_mat)

        # Mensaje de error / éxito
        self.lbl_mensaje = QLabel("")
        self.lbl_mensaje.setObjectName("lbl_error")
        self.lbl_mensaje.setWordWrap(True)
        form_layout.addWidget(self.lbl_mensaje)

        form_layout.addStretch()
        scroll.setWidget(contenido)
        layout.addWidget(scroll, stretch=1)

        layout.addSpacing(12)

        # ── Botones ──────────────────────────────────────────
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

    # ── Carga de datos (modo edición) ────────────────────────

    def _cargar_datos(self, id_vehiculo: int):
        """Rellena el formulario con datos del vehículo existente."""
        veh = ModeloVehiculo.obtener_por_id(id_vehiculo)
        if not veh:
            return

        self.inp_placa.setText(veh["placa"])
        self.inp_placa.setReadOnly(True)           # La placa no se cambia
        self.inp_propietario.setText(veh["propietario"])
        self.inp_conductor.setText(veh["conductor"])
        idx = self.cbo_tipo.findText(veh["tipo_vehiculo"], Qt.MatchFixedString)
        if idx >= 0:
            self.cbo_tipo.setCurrentIndex(idx)

        # Cargar fechas de matrículas
        matriculas = ModeloMatricula.obtener_por_vehiculo(id_vehiculo)
        for m in matriculas:
            tipo = m["tipo"]
            fecha = m["fecha_vencimiento"]
            if tipo in self.date_inputs and fecha:
                if hasattr(fecha, "year"):
                    q_date = QDate(fecha.year, fecha.month, fecha.day)
                else:
                    partes = str(fecha).split("-")
                    q_date = QDate(int(partes[0]), int(partes[1]), int(partes[2]))
                self.date_inputs[tipo].setDate(q_date)

    # ── Guardar ──────────────────────────────────────────────

    def _guardar(self):
        """Valida y guarda el vehículo con sus matrículas."""
        placa       = self.inp_placa.text().strip().upper()
        propietario = self.inp_propietario.text().strip()
        conductor   = self.inp_conductor.text().strip()
        tipo_veh    = self.cbo_tipo.currentText()

        if not placa or not propietario or not conductor:
            self._mostrar_error("Por favor completa los campos obligatorios.")
            return

        if self.id_vehiculo is None:
            # ── Modo Crear ───────────────────────────────────
            if ModeloVehiculo.obtener_por_placa(placa):
                self._mostrar_error("Ya existe un vehículo con esa placa.")
                return

            id_veh = ModeloVehiculo.crear(placa, propietario, conductor, tipo_veh)
            if id_veh == -1:
                self._mostrar_error("Error al guardar en la base de datos.")
                return
        else:
            # ── Modo Editar ──────────────────────────────────
            id_veh = self.id_vehiculo
            ok = ModeloVehiculo.actualizar(
                id_veh, placa, propietario, conductor, tipo_veh
            )
            if not ok:
                self._mostrar_error("Error al actualizar el vehículo.")
                return

        # Guardar matrículas
        fechas = {}
        for tipo, date_edit in self.date_inputs.items():
            qd = date_edit.date()
            from datetime import date
            fechas[tipo] = date(qd.year(), qd.month(), qd.day())

        ModeloMatricula.guardar_todas(id_veh, fechas)

        self.lbl_mensaje.setObjectName("lbl_exito")
        self.lbl_mensaje.setText("✅ Vehículo guardado correctamente.")
        self.guardado.emit()

    def _mostrar_error(self, msg: str):
        self.lbl_mensaje.setObjectName("lbl_error")
        self.lbl_mensaje.setText(f"⚠ {msg}")


# ══════════════════════════════════════════════════════════════
# Sub-vista: Lista de vehículos
# ══════════════════════════════════════════════════════════════

class ListaVehiculos(QWidget):
    """Tabla con todos los vehículos registrados."""

    solicitar_editar      = pyqtSignal(int)
    solicitar_inhabilitar = pyqtSignal(int, str)  # id, placa

    def __init__(self):
        super().__init__()
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        lbl = QLabel("Lista de vehículos registrados")
        lbl.setObjectName("titulo_modulo")
        lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(lbl)

        # Tabla
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
        self.tabla.setStyleSheet("""
            QTableWidget { alternate-background-color: #F9FAFC; }
        """)
        layout.addWidget(self.tabla)

    def actualizar(self):
        """Recarga los datos de la tabla."""
        vehiculos = ModeloVehiculo.listar_todos()
        self.tabla.setRowCount(len(vehiculos))

        for fila, v in enumerate(vehiculos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(v["placa"]))
            self.tabla.setItem(fila, 1, QTableWidgetItem(v["propietario"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(v["conductor"]))
            self.tabla.setItem(fila, 3, QTableWidgetItem(v["tipo_vehiculo"]))

            # Estado
            estado = "Habilitado" if v["habilitado"] else "Inhabilitado"
            item_estado = QTableWidgetItem(estado)
            item_estado.setForeground(
                QColor("#27AE60") if v["habilitado"] else QColor("#E74C3C")
            )
            self.tabla.setItem(fila, 4, item_estado)

            # Acciones
            widget_acc = QWidget()
            fila_acc = QHBoxLayout(widget_acc)
            fila_acc.setContentsMargins(4, 2, 4, 2)
            fila_acc.setSpacing(6)

            btn_editar = QPushButton("Editar")
            btn_editar.setObjectName("btn_secundario")
            btn_editar.setFixedHeight(28)
            btn_editar.setCursor(Qt.PointingHandCursor)
            id_v = v["id_vehiculo"]
            btn_editar.clicked.connect(lambda _, i=id_v: self.solicitar_editar.emit(i))
            fila_acc.addWidget(btn_editar)

            if v["habilitado"]:
                btn_inh = QPushButton("Inhabilitar")
                btn_inh.setObjectName("btn_peligro")
                btn_inh.setFixedHeight(28)
                btn_inh.setCursor(Qt.PointingHandCursor)
                placa_v = v["placa"]
                btn_inh.clicked.connect(
                    lambda _, i=id_v, p=placa_v:
                    self.solicitar_inhabilitar.emit(i, p)
                )
                fila_acc.addWidget(btn_inh)
            else:
                btn_hab = QPushButton("Habilitar")
                btn_hab.setObjectName("btn_exito")
                btn_hab.setFixedHeight(28)
                btn_hab.setCursor(Qt.PointingHandCursor)
                btn_hab.clicked.connect(
                    lambda _, i=id_v: self._habilitar(i)
                )
                fila_acc.addWidget(btn_hab)

            self.tabla.setCellWidget(fila, 5, widget_acc)
            self.tabla.setRowHeight(fila, 44)

    def _habilitar(self, id_vehiculo: int):
        resp = QMessageBox.question(
            self, "Confirmar",
            "¿Deseas habilitar este vehículo nuevamente?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if resp == QMessageBox.Yes:
            ModeloVehiculo.habilitar(id_vehiculo)
            self.actualizar()


# ══════════════════════════════════════════════════════════════
# Vista principal del módulo de Vehículos
# ══════════════════════════════════════════════════════════════

class VistaVehiculos(QWidget):
    """
    Módulo de gestión de vehículos.
    Contiene sub-vistas: menú, formulario y lista.
    """

    def __init__(self):
        super().__init__()
        self._construir_ui()

    def _construir_ui(self):
        self.layout_raiz = QVBoxLayout(self)
        self.layout_raiz.setContentsMargins(32, 28, 32, 28)
        self.layout_raiz.setSpacing(0)

        # Título módulo
        lbl_mod = QLabel("Módulo de gestión de vehículos")
        lbl_mod.setObjectName("titulo_modulo")
        lbl_mod.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.layout_raiz.addWidget(lbl_mod)

        layout_sub = QLabel("Opciones  ·  Selecciona la acción que desees realizar")
        layout_sub.setObjectName("subtitulo_modulo")
        self.layout_raiz.addWidget(layout_sub)

        self.layout_raiz.addSpacing(16)

        # Stack interno (menú opciones / formulario / lista)
        self.stack = QStackedWidget()
        self.layout_raiz.addWidget(self.stack, stretch=1)

        # ── Página 0: Menú de opciones ──────────────────────
        pagina_menu = self._crear_pagina_menu()
        self.stack.addWidget(pagina_menu)

        # ── Página 1: Formulario registrar ──────────────────
        self.form_registrar = FormularioVehiculo()
        self.form_registrar.guardado.connect(self._tras_guardar)
        self.form_registrar.cancelado.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.form_registrar)

        # ── Página 2: Lista de vehículos ────────────────────
        self.lista_veh = ListaVehiculos()
        self.lista_veh.solicitar_editar.connect(self._abrir_editar)
        self.lista_veh.solicitar_inhabilitar.connect(self._inhabilitar_vehiculo)
        self.stack.addWidget(self.lista_veh)

        # ── Página 3: Formulario editar (se crea al vuelo) ──
        self._pagina_editar_idx = 3
        # Placeholder; se reemplaza en _abrir_editar
        self.stack.addWidget(QWidget())

    def _crear_pagina_menu(self) -> QWidget:
        """Construye el menú principal con tarjetas de opciones."""
        pagina = QWidget()
        pagina.setStyleSheet("background: transparent;")
        lyt = QVBoxLayout(pagina)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(16)

        opciones = [
            ("🚗", "Registrar y editar vehículos",
             "Módulo para registrar datos del vehículo (placa, propietario, conductor,\n"
             "tipo de vehículo, capacidad de carga, documentos relacionados,\n"
             "contrato de vinculación (opcional)).",
             [("Registrar", self._abrir_registrar),
              ("Ver lista", lambda: self._ir_lista())]),

            ("🔍", "Verificación de matrículas",
             "Módulo para visualizar todas las matrículas asociadas a los vehículos,\n"
             "fechas de vencimiento y opción de agregar comprobantes de pago.",
             [("Verificar", self._ir_matriculas)]),

            ("🚫", "Vehículos inhabilitados",
             "En caso de inhabilitar el servicio de un vehículo, acá se podrá visualizar\n"
             "con qué vehículos no se podrá contar. Con la opción de habilitarlos\n"
             "cuando ya se pueda contar con ellos.",
             [("Visualizar", self._ir_lista)]),
        ]

        for icono, titulo, desc, btns in opciones:
            card = self._crear_card_opcion(icono, titulo, desc, btns)
            lyt.addWidget(card)

        lyt.addStretch()
        return pagina

    @staticmethod
    def _crear_card_opcion(icono, titulo, desc, botones) -> QFrame:
        """Crea una tarjeta de opción del menú."""
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
        lbl_ico.setStyleSheet(
            "background: #FFFBEA; border-radius: 32px;"
        )
        lyt.addWidget(lbl_ico)

        # Texto
        col_texto = QVBoxLayout()
        col_texto.setSpacing(4)

        lbl_tit = QLabel(titulo)
        lbl_tit.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_tit.setStyleSheet("color: #1E2027;")
        col_texto.addWidget(lbl_tit)

        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet("color: #6B7080; font-size: 12px;")
        lbl_desc.setWordWrap(True)
        col_texto.addWidget(lbl_desc)

        # Botones inline
        fila_btns = QHBoxLayout()
        fila_btns.setSpacing(8)
        for texto, accion in botones:
            btn = QPushButton(texto)
            btn.setObjectName("btn_secundario")
            btn.setFixedHeight(32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(accion)
            fila_btns.addWidget(btn)
        fila_btns.addStretch()
        col_texto.addLayout(fila_btns)

        lyt.addLayout(col_texto, stretch=1)
        return card

    # ── Navegación interna ───────────────────────────────────

    def _abrir_registrar(self):
        # Recrear el formulario para asegurarse de que está limpio
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
        """Navega al módulo de Matrículas (se hace desde la ventana principal)."""
        # Buscamos la ventana principal en la jerarquía
        ventana = self.window()
        if hasattr(ventana, '_navegar'):
            ventana._navegar(2)

    def _abrir_editar(self, id_vehiculo: int):
        """Abre el formulario en modo edición para el vehículo dado."""
        form_editar = FormularioVehiculo(id_vehiculo=id_vehiculo)
        form_editar.guardado.connect(self._tras_guardar_edicion)
        form_editar.cancelado.connect(lambda: self.stack.setCurrentIndex(2))
        # Reemplazar página 3
        widget_actual = self.stack.widget(self._pagina_editar_idx)
        if widget_actual:
            self.stack.removeWidget(widget_actual)
            widget_actual.deleteLater()
        self.stack.insertWidget(self._pagina_editar_idx, form_editar)
        self.stack.setCurrentIndex(self._pagina_editar_idx)

    def _tras_guardar(self):
        """Callback después de registrar un vehículo nuevo."""
        self.stack.setCurrentIndex(0)

    def _tras_guardar_edicion(self):
        """Callback después de editar un vehículo."""
        self.lista_veh.actualizar()
        self.stack.setCurrentIndex(2)

    def _inhabilitar_vehiculo(self, id_vehiculo: int, placa: str):
        """Pide confirmación y ejecuta la inhabilitación."""
        from PyQt5.QtWidgets import QInputDialog
        motivo, ok = QInputDialog.getText(
            self, "Inhabilitar vehículo",
            f"¿Motivo para inhabilitar {placa}? (opcional):",
        )
        if ok:
            ModeloVehiculo.inhabilitar(id_vehiculo, motivo)
            self.lista_veh.actualizar()

    def cargar_lista(self):
        """Llamado desde la ventana principal al cambiar de módulo."""
        pass   # La lista se carga solo cuando el usuario la pide
