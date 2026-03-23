"""
============================================================
SIGAOT - Vista del Módulo de Personal
Archivo: vistas/vista_personal.py
Funciones:
  - Registrar personal (nombre, ID, teléfono, correo, rol,
    imagen de cédula, y opcionalmente usuario+contraseña)
  - Tabla con todo el personal activo
  - Panel de detalle al seleccionar una fila
  - Botón de regreso en cada sub-vista
============================================================
"""

import os
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QScrollArea, QSizePolicy, QAbstractItemView,
    QFormLayout, QGroupBox, QFileDialog, QCheckBox,
    QSplitter,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

from modelos.personal import ModeloPersonal
from modelos.usuario  import ModeloUsuario

# Ruta donde se guardan las imágenes de cédulas
RUTA_CEDULAS = r"C:\Users\Lenovo\Desktop\Vehículos\Personal\Cedulas"


# ══════════════════════════════════════════════════════════════
# Formulario Registrar / Editar personal
# ══════════════════════════════════════════════════════════════
class FormularioPersonal(QWidget):
    """
    Formulario para registrar o editar un miembro del personal.
    Emite `guardado` o `cancelado` al terminar.
    """

    guardado  = pyqtSignal()
    cancelado = pyqtSignal()

    def __init__(self, id_personal: int = None):
        super().__init__()
        self.id_personal  = id_personal
        self._ruta_imagen = None
        self._construir_ui()
        if id_personal:
            self._cargar_datos(id_personal)

    # ── UI ───────────────────────────────────────────────────

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Encabezado con botón regreso ─────────────────────
        enc = QHBoxLayout()
        enc.setSpacing(14)

        btn_back = QPushButton("← Volver")
        btn_back.setObjectName("btn_secundario")
        btn_back.setFixedHeight(32)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.cancelado.emit)
        enc.addWidget(btn_back)

        titulo = "Registrar Personal" if not self.id_personal else "Editar Personal"
        lbl_tit = QLabel(titulo)
        lbl_tit.setObjectName("titulo_modulo")
        lbl_tit.setFont(QFont("Segoe UI", 20, QFont.Bold))
        enc.addWidget(lbl_tit, stretch=1)
        layout.addLayout(enc)
        layout.addSpacing(16)

        # ── Scroll ───────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        contenido = QWidget()
        contenido.setStyleSheet("background: transparent;")
        form_lyt = QVBoxLayout(contenido)
        form_lyt.setContentsMargins(0, 0, 20, 0)
        form_lyt.setSpacing(14)

        estilo_grp = """
            QGroupBox {
                font-weight: bold; font-size: 13px;
                border: 1.5px solid #E0E3E8;
                border-radius: 8px;
                margin-top: 8px; padding-top: 12px;
                background: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px; color: #4A5060;
            }
        """

        # ── Datos personales ─────────────────────────────────
        grp_datos = QGroupBox("Datos personales")
        grp_datos.setStyleSheet(estilo_grp)
        g_lyt = QFormLayout(grp_datos)
        g_lyt.setContentsMargins(16, 20, 16, 16)
        g_lyt.setSpacing(12)
        g_lyt.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.inp_nombre   = QLineEdit()
        self.inp_nombre.setPlaceholderText("Nombre completo")
        self.inp_nombre.setFixedHeight(36)

        self.inp_id = QLineEdit()
        self.inp_id.setPlaceholderText("Número de cédula o NIT")
        self.inp_id.setFixedHeight(36)

        self.inp_telefono = QLineEdit()
        self.inp_telefono.setPlaceholderText("Ej: 310 123 4567")
        self.inp_telefono.setFixedHeight(36)

        self.inp_correo = QLineEdit()
        self.inp_correo.setPlaceholderText("correo@ejemplo.com")
        self.inp_correo.setFixedHeight(36)

        self.cbo_rol = QComboBox()
        self.cbo_rol.setFixedHeight(36)
        self._cargar_roles()

        g_lyt.addRow("Nombre completo *:", self.inp_nombre)
        g_lyt.addRow("Identificación *:", self.inp_id)
        g_lyt.addRow("Teléfono:", self.inp_telefono)
        g_lyt.addRow("Correo:", self.inp_correo)
        g_lyt.addRow("Rol:", self.cbo_rol)
        form_lyt.addWidget(grp_datos)

        # ── Imagen de cédula ─────────────────────────────────
        grp_img = QGroupBox("Imagen de cédula (opcional)")
        grp_img.setStyleSheet(estilo_grp)
        img_lyt = QVBoxLayout(grp_img)
        img_lyt.setContentsMargins(16, 20, 16, 16)
        img_lyt.setSpacing(10)

        fila_img = QHBoxLayout()
        fila_img.setSpacing(12)

        self.lbl_preview = QLabel("Sin imagen\nseleccionada")
        self.lbl_preview.setFixedSize(130, 90)
        self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("""
            background: #F4F5F7;
            border: 1.5px dashed #C0C4D0;
            border-radius: 6px;
            color: #9099A8; font-size: 11px;
        """)
        fila_img.addWidget(self.lbl_preview)

        col_img = QVBoxLayout()
        col_img.setSpacing(8)

        self.lbl_nombre_img = QLabel("Ningún archivo seleccionado")
        self.lbl_nombre_img.setStyleSheet("color: #6B7080; font-size: 12px;")
        self.lbl_nombre_img.setWordWrap(True)
        col_img.addWidget(self.lbl_nombre_img)

        btn_sel_img = QPushButton("📎  Seleccionar imagen")
        btn_sel_img.setObjectName("btn_secundario")
        btn_sel_img.setFixedHeight(34)
        btn_sel_img.setCursor(Qt.PointingHandCursor)
        btn_sel_img.clicked.connect(self._seleccionar_imagen)
        col_img.addWidget(btn_sel_img)
        col_img.addStretch()

        fila_img.addLayout(col_img, stretch=1)
        img_lyt.addLayout(fila_img)
        form_lyt.addWidget(grp_img)

        # ── Acceso al sistema (opcional) ─────────────────────
        grp_acceso = QGroupBox("Acceso al sistema (opcional)")
        grp_acceso.setStyleSheet(estilo_grp)
        acc_lyt = QVBoxLayout(grp_acceso)
        acc_lyt.setContentsMargins(16, 20, 16, 16)
        acc_lyt.setSpacing(12)

        self.chk_crear_usuario = QCheckBox(
            "Crear usuario de acceso para esta persona"
        )
        self.chk_crear_usuario.setStyleSheet("font-size: 13px;")
        self.chk_crear_usuario.toggled.connect(self._toggle_acceso)
        acc_lyt.addWidget(self.chk_crear_usuario)

        self.widget_acceso = QWidget()
        self.widget_acceso.setVisible(False)
        wf = QFormLayout(self.widget_acceso)
        wf.setContentsMargins(0, 4, 0, 0)
        wf.setSpacing(12)
        wf.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.inp_usu = QLineEdit()
        self.inp_usu.setPlaceholderText("Nombre de usuario")
        self.inp_usu.setFixedHeight(36)

        self.inp_pw = QLineEdit()
        self.inp_pw.setPlaceholderText("Contraseña")
        self.inp_pw.setEchoMode(QLineEdit.Password)
        self.inp_pw.setFixedHeight(36)

        self.inp_pw2 = QLineEdit()
        self.inp_pw2.setPlaceholderText("Confirmar contraseña")
        self.inp_pw2.setEchoMode(QLineEdit.Password)
        self.inp_pw2.setFixedHeight(36)

        wf.addRow("Usuario:", self.inp_usu)
        wf.addRow("Contraseña:", self.inp_pw)
        wf.addRow("Confirmar:", self.inp_pw2)
        acc_lyt.addWidget(self.widget_acceso)
        form_lyt.addWidget(grp_acceso)

        # Mensaje de estado
        self.lbl_msg = QLabel("")
        self.lbl_msg.setWordWrap(True)
        self.lbl_msg.setStyleSheet("color: #E74C3C; font-size: 12px;")
        form_lyt.addWidget(self.lbl_msg)
        form_lyt.addStretch()

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

        btn_guardar = QPushButton("Guardar ✓")
        btn_guardar.setObjectName("btn_primario")
        btn_guardar.setFixedHeight(38)
        btn_guardar.setMinimumWidth(140)
        btn_guardar.setCursor(Qt.PointingHandCursor)
        btn_guardar.clicked.connect(self._guardar)
        fila_btns.addWidget(btn_guardar)

        layout.addLayout(fila_btns)

    # ── Helpers ──────────────────────────────────────────────

    def _cargar_roles(self):
        self.cbo_rol.clear()
        self._roles = ModeloPersonal.listar_roles()
        for r in self._roles:
            self.cbo_rol.addItem(r["nombre_rol"], r["id_rol"])

    def _toggle_acceso(self, activo: bool):
        self.widget_acceso.setVisible(activo)

    def _seleccionar_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Imagen de cédula", "",
            "Imágenes y PDF (*.png *.jpg *.jpeg *.bmp *.tiff *.pdf)"
        )
        if not ruta:
            return
        self._ruta_imagen = ruta
        self.lbl_nombre_img.setText(os.path.basename(ruta))
        if ruta.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            pix = QPixmap(ruta).scaled(
                130, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.lbl_preview.setPixmap(pix)
            self.lbl_preview.setText("")
        else:
            self.lbl_preview.setText("📄 PDF\nseleccionado")

    def _cargar_datos(self, id_personal: int):
        p = ModeloPersonal.obtener_por_id(id_personal)
        if not p:
            return
        self.inp_nombre.setText(p.get("nombre_completo", ""))
        self.inp_id.setText(p.get("numero_id", ""))
        self.inp_telefono.setText(p.get("telefono") or "")
        self.inp_correo.setText(p.get("correo") or "")

        id_rol = p.get("id_rol")
        for i in range(self.cbo_rol.count()):
            if self.cbo_rol.itemData(i) == id_rol:
                self.cbo_rol.setCurrentIndex(i)
                break

        ruta_img = p.get("ruta_imagen_cedula")
        if ruta_img and os.path.exists(ruta_img):
            self._ruta_imagen = ruta_img
            self.lbl_nombre_img.setText(os.path.basename(ruta_img))
            if ruta_img.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                pix = QPixmap(ruta_img).scaled(
                    130, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.lbl_preview.setPixmap(pix)

    # ── Guardar ──────────────────────────────────────────────

    def _guardar(self):
        nombre    = self.inp_nombre.text().strip()
        numero_id = self.inp_id.text().strip()
        telefono  = self.inp_telefono.text().strip()
        correo    = self.inp_correo.text().strip()
        id_rol    = self.cbo_rol.currentData()

        if not nombre or not numero_id:
            self.lbl_msg.setText("⚠  Los campos marcados con * son obligatorios.")
            return

        # Copiar imagen si se seleccionó
        ruta_guardada = None
        if self._ruta_imagen:
            try:
                os.makedirs(RUTA_CEDULAS, exist_ok=True)
                ext = os.path.splitext(self._ruta_imagen)[1]
                destino = os.path.join(RUTA_CEDULAS, f"{numero_id}{ext}")
                shutil.copy2(self._ruta_imagen, destino)
                ruta_guardada = destino
            except Exception as e:
                print(f"[Personal] Error al copiar imagen: {e}")

        if self.id_personal is None:
            id_nuevo = ModeloPersonal.crear(
                nombre, numero_id, telefono, correo,
                id_rol, ruta_guardada
            )
            if id_nuevo == -1:
                self.lbl_msg.setText(
                    "⚠  Error al guardar. El número de identificación "
                    "podría estar duplicado."
                )
                return

            # Crear usuario si se marcó
            if self.chk_crear_usuario.isChecked():
                usu = self.inp_usu.text().strip()
                pw  = self.inp_pw.text()
                pw2 = self.inp_pw2.text()
                if usu and pw:
                    if pw != pw2:
                        self.lbl_msg.setText(
                            "✅  Personal guardado, pero las contraseñas no "
                            "coinciden. Edita el registro para crear el acceso."
                        )
                        self.guardado.emit()
                        return
                    ModeloUsuario.crear(usu, pw, id_rol, id_nuevo)
        else:
            ok = ModeloPersonal.actualizar(
                self.id_personal, nombre, numero_id,
                telefono, correo, id_rol, ruta_guardada
            )
            if not ok:
                self.lbl_msg.setText("⚠  Error al actualizar el registro.")
                return

        self.guardado.emit()


# ══════════════════════════════════════════════════════════════
# Panel de detalle del personal seleccionado
# ══════════════════════════════════════════════════════════════
class PanelDetalle(QFrame):
    """Panel derecho que muestra el detalle de una persona."""

    solicitar_editar = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card {
                background: #FFFFFF;
                border: 1.5px solid #E0E3E8;
                border-radius: 10px;
            }
            QLabel { border: none; background: transparent; }
        """)
        self.setMinimumWidth(260)
        self._id_actual = None
        self._construir_ui()

    def _construir_ui(self):
        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(20, 20, 20, 20)
        lyt.setSpacing(10)

        # Foto de cédula
        self.lbl_foto = QLabel("Sin imagen\nde cédula")
        self.lbl_foto.setFixedSize(170, 115)
        self.lbl_foto.setAlignment(Qt.AlignCenter)
        self.lbl_foto.setStyleSheet("""
            background: #F4F5F7;
            border: 1.5px dashed #C0C4D0 !important;
            border-radius: 8px;
            color: #9099A8; font-size: 11px;
        """)
        lyt.addWidget(self.lbl_foto, alignment=Qt.AlignHCenter)

        # Nombre
        self.lbl_nombre = QLabel("Selecciona una persona")
        self.lbl_nombre.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.lbl_nombre.setStyleSheet("color: #1E2027;")
        self.lbl_nombre.setWordWrap(True)
        self.lbl_nombre.setAlignment(Qt.AlignCenter)
        lyt.addWidget(self.lbl_nombre)

        # Chip de rol
        self.lbl_rol = QLabel("")
        self.lbl_rol.setAlignment(Qt.AlignCenter)
        self.lbl_rol.setStyleSheet("""
            background: #FFF8D6;
            color: #8A6800;
            border-radius: 8px;
            padding: 3px 14px;
            font-size: 11px;
            font-weight: bold;
        """)
        lyt.addWidget(self.lbl_rol, alignment=Qt.AlignHCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #E0E3E8; max-height: 1px;")
        lyt.addWidget(sep)

        # Campos de datos
        self.campos: dict[str, QLabel] = {}
        filas = [
            ("id_doc",   "📋  Identificación"),
            ("telefono", "📞  Teléfono"),
            ("correo",   "✉   Correo electrónico"),
            ("registro", "📅  Fecha de registro"),
        ]
        for clave, etiqueta in filas:
            lbl_et = QLabel(etiqueta)
            lbl_et.setStyleSheet("color: #6B7080; font-size: 11px;")
            lyt.addWidget(lbl_et)

            lbl_val = QLabel("—")
            lbl_val.setStyleSheet(
                "color: #1E2027; font-size: 13px; font-weight: bold;"
            )
            lbl_val.setWordWrap(True)
            lyt.addWidget(lbl_val)
            self.campos[clave] = lbl_val

        lyt.addStretch()

        self.btn_editar = QPushButton("✏  Editar registro")
        self.btn_editar.setObjectName("btn_primario")
        self.btn_editar.setFixedHeight(36)
        self.btn_editar.setCursor(Qt.PointingHandCursor)
        self.btn_editar.setVisible(False)
        self.btn_editar.clicked.connect(
            lambda: self.solicitar_editar.emit(self._id_actual)
        )
        lyt.addWidget(self.btn_editar)

    def mostrar(self, datos: dict):
        self._id_actual = datos.get("id_personal")

        # Imagen
        ruta_img = datos.get("ruta_imagen_cedula")
        if ruta_img and os.path.exists(ruta_img):
            if ruta_img.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                pix = QPixmap(ruta_img).scaled(
                    170, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.lbl_foto.setPixmap(pix)
                self.lbl_foto.setText("")
            else:
                self.lbl_foto.clear()
                self.lbl_foto.setText("📄 Cédula PDF")
        else:
            self.lbl_foto.clear()
            self.lbl_foto.setText("Sin imagen\nde cédula")

        self.lbl_nombre.setText(datos.get("nombre_completo", "—"))
        self.lbl_rol.setText(datos.get("nombre_rol") or "Sin rol")

        fecha_reg = datos.get("fecha_registro", "")
        if hasattr(fecha_reg, "strftime"):
            fecha_str = fecha_reg.strftime("%d/%m/%Y")
        else:
            fecha_str = str(fecha_reg)[:10] if fecha_reg else "—"

        self.campos["id_doc"].setText(datos.get("numero_id", "—"))
        self.campos["telefono"].setText(datos.get("telefono") or "—")
        self.campos["correo"].setText(datos.get("correo") or "—")
        self.campos["registro"].setText(fecha_str)
        self.btn_editar.setVisible(True)

    def limpiar(self):
        self._id_actual = None
        self.lbl_foto.clear()
        self.lbl_foto.setText("Sin imagen\nde cédula")
        self.lbl_nombre.setText("Selecciona una persona")
        self.lbl_rol.setText("")
        for lbl in self.campos.values():
            lbl.setText("—")
        self.btn_editar.setVisible(False)


# ══════════════════════════════════════════════════════════════
# Sub-vista: Tabla de personal con detalle
# ══════════════════════════════════════════════════════════════
class TablaPersonal(QWidget):
    """Tabla de personal con panel de detalle en splitter."""

    solicitar_editar  = pyqtSignal(int)
    solicitar_agregar = pyqtSignal()
    ir_menu           = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._personal_data = []
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Encabezado
        enc = QHBoxLayout()
        btn_back = QPushButton("← Volver")
        btn_back.setObjectName("btn_secundario")
        btn_back.setFixedHeight(32)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.ir_menu.emit)
        enc.addWidget(btn_back)

        lbl = QLabel("Personal registrado")
        lbl.setObjectName("titulo_modulo")
        lbl.setFont(QFont("Segoe UI", 20, QFont.Bold))
        enc.addWidget(lbl, stretch=1)

        btn_nuevo = QPushButton("+ Agregar personal")
        btn_nuevo.setObjectName("btn_primario")
        btn_nuevo.setFixedHeight(34)
        btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self.solicitar_agregar.emit)
        enc.addWidget(btn_nuevo)
        layout.addLayout(enc)

        # Splitter tabla | detalle
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(4)
        splitter.setStyleSheet(
            "QSplitter::handle { background: #E0E3E8; }"
        )

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Nombre completo", "Identificación",
            "Teléfono", "Correo", "Rol",
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
        self.tabla.itemSelectionChanged.connect(self._al_seleccionar)
        splitter.addWidget(self.tabla)

        self.panel_detalle = PanelDetalle()
        self.panel_detalle.solicitar_editar.connect(self.solicitar_editar)
        splitter.addWidget(self.panel_detalle)

        splitter.setSizes([680, 300])
        layout.addWidget(splitter, stretch=1)

    def actualizar(self):
        self._personal_data = ModeloPersonal.listar()
        self.tabla.setRowCount(len(self._personal_data))
        for fila, p in enumerate(self._personal_data):
            self.tabla.setItem(fila, 0, QTableWidgetItem(p["nombre_completo"]))
            self.tabla.setItem(fila, 1, QTableWidgetItem(p["numero_id"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(p.get("telefono") or "—"))
            self.tabla.setItem(fila, 3, QTableWidgetItem(p.get("correo") or "—"))
            self.tabla.setItem(fila, 4, QTableWidgetItem(p.get("nombre_rol") or "—"))
            self.tabla.setRowHeight(fila, 40)
        self.panel_detalle.limpiar()

    def _al_seleccionar(self):
        fila_idx = self.tabla.currentRow()
        if 0 <= fila_idx < len(self._personal_data):
            self.panel_detalle.mostrar(self._personal_data[fila_idx])
        else:
            self.panel_detalle.limpiar()


# ══════════════════════════════════════════════════════════════
# Vista principal del módulo Personal
# ══════════════════════════════════════════════════════════════
class VistaPersonal(QWidget):
    """
    Módulo de gestión de personal.
    Stack interno:
      0 – Menú de opciones
      1 – Formulario registrar
      2 – Tabla con detalle
      3 – Formulario editar (creado al vuelo)
    """

    def __init__(self):
        super().__init__()
        self._pagina_editar = 3
        self._construir_ui()

    def _construir_ui(self):
        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(32, 28, 32, 28)
        raiz.setSpacing(0)

        # Encabezado del módulo
        lbl_mod = QLabel("Módulo de Personal")
        lbl_mod.setObjectName("titulo_modulo")
        lbl_mod.setFont(QFont("Segoe UI", 22, QFont.Bold))
        raiz.addWidget(lbl_mod)

        lbl_sub = QLabel("Gestión del equipo  ·  Selecciona una acción")
        lbl_sub.setObjectName("subtitulo_modulo")
        raiz.addWidget(lbl_sub)
        raiz.addSpacing(16)

        self.stack = QStackedWidget()
        raiz.addWidget(self.stack, stretch=1)

        # Página 0: Menú
        self.stack.addWidget(self._crear_menu())

        # Página 1: Formulario registrar
        self.form_reg = FormularioPersonal()
        self.form_reg.guardado.connect(self._tras_guardar)
        self.form_reg.cancelado.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.form_reg)

        # Página 2: Tabla
        self.tabla_personal = TablaPersonal()
        self.tabla_personal.solicitar_agregar.connect(self._abrir_registrar)
        self.tabla_personal.solicitar_editar.connect(self._abrir_editar)
        self.tabla_personal.ir_menu.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.tabla_personal)

        # Página 3: Formulario editar (placeholder)
        self.stack.addWidget(QWidget())

    # ── Menú ─────────────────────────────────────────────────

    def _crear_menu(self) -> QWidget:
        pagina = QWidget()
        pagina.setStyleSheet("background: transparent;")
        lyt = QVBoxLayout(pagina)
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.setSpacing(16)

        opciones = [
            ("👤", "Registrar personal",
             "Agrega un nuevo miembro al equipo: datos personales, rol,\n"
             "imagen de cédula y opcionalmente acceso al sistema.",
             "Registrar", self._abrir_registrar),
            ("📋", "Ver personal registrado",
             "Lista completa con panel de detalle individual\n"
             "para editar o consultar cada registro.",
             "Ver personal", self._ir_tabla),
        ]
        for icono, titulo, desc, txt_btn, accion in opciones:
            lyt.addWidget(self._crear_card(icono, titulo, desc, txt_btn, accion))

        lyt.addStretch()
        return pagina

    @staticmethod
    def _crear_card(icono, titulo, desc, txt_btn, accion) -> QFrame:
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

        lbl_tit = QLabel(titulo)
        lbl_tit.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_tit.setStyleSheet("color: #1E2027;")
        col.addWidget(lbl_tit)

        lbl_desc = QLabel(desc)
        lbl_desc.setStyleSheet("color: #6B7080; font-size: 12px;")
        lbl_desc.setWordWrap(True)
        col.addWidget(lbl_desc)

        fila_btn = QHBoxLayout()
        btn = QPushButton(txt_btn)
        btn.setObjectName("btn_secundario")
        btn.setFixedHeight(32)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(accion)
        fila_btn.addWidget(btn)
        fila_btn.addStretch()
        col.addLayout(fila_btn)

        lyt.addLayout(col, stretch=1)
        return card

    # ── Navegación interna ───────────────────────────────────

    def _abrir_registrar(self):
        self.stack.removeWidget(self.form_reg)
        self.form_reg.deleteLater()
        self.form_reg = FormularioPersonal()
        self.form_reg.guardado.connect(self._tras_guardar)
        self.form_reg.cancelado.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.insertWidget(1, self.form_reg)
        self.stack.setCurrentIndex(1)

    def _ir_tabla(self):
        self.tabla_personal.actualizar()
        self.stack.setCurrentIndex(2)

    def _abrir_editar(self, id_personal: int):
        form = FormularioPersonal(id_personal=id_personal)
        form.guardado.connect(self._tras_guardar_edicion)
        form.cancelado.connect(lambda: self.stack.setCurrentIndex(2))

        old = self.stack.widget(self._pagina_editar)
        if old:
            self.stack.removeWidget(old)
            old.deleteLater()
        self.stack.insertWidget(self._pagina_editar, form)
        self.stack.setCurrentIndex(self._pagina_editar)

    def _tras_guardar(self):
        QMessageBox.information(
            self, "Guardado", "✅  Personal guardado correctamente."
        )
        self.stack.setCurrentIndex(0)

    def _tras_guardar_edicion(self):
        QMessageBox.information(
            self, "Actualizado", "✅  Registro actualizado correctamente."
        )
        self.tabla_personal.actualizar()
        self.stack.setCurrentIndex(2)
