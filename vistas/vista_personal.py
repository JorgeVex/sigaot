"""
============================================================
SIGAOT - Vista del Módulo de Personal
Archivo: vistas/vista_personal.py
Campos reales BD: fecha_nacimiento, tipo_sangre
Alertas de cumpleaños basadas en fecha_nacimiento
============================================================
"""

import os
import shutil
from datetime import date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QLineEdit, QComboBox, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QScrollArea, QAbstractItemView, QFormLayout, QGroupBox,
    QFileDialog, QCheckBox, QSplitter,
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QColor

from modelos.personal import ModeloPersonal
from modelos.usuario  import ModeloUsuario

RUTA_CEDULAS = r"C:\Users\Lenovo\Desktop\Vehiculos\Personal\Cedulas"
DIAS_ALERTA  = 5

TIPOS_SANGRE = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]


# ══════════════════════════════════════════════════════════════
# Formulario Registrar / Editar
# ══════════════════════════════════════════════════════════════
class FormularioPersonal(QWidget):

    guardado  = pyqtSignal()
    cancelado = pyqtSignal()

    def __init__(self, id_personal: int = None):
        super().__init__()
        self.id_personal  = id_personal
        self._ruta_imagen = None
        self._construir_ui()
        if id_personal:
            self._cargar_datos(id_personal)

    def _construir_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Encabezado
        enc = QHBoxLayout(); enc.setSpacing(14)
        btn_back = QPushButton("← Volver")
        btn_back.setObjectName("btn_secundario")
        btn_back.setFixedHeight(32); btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.cancelado.emit)
        enc.addWidget(btn_back)
        lbl_tit = QLabel("Registrar Personal" if not self.id_personal else "Editar Personal")
        lbl_tit.setObjectName("titulo_modulo")
        lbl_tit.setFont(QFont("Segoe UI", 20, QFont.Bold))
        enc.addWidget(lbl_tit, stretch=1)
        layout.addLayout(enc)
        layout.addSpacing(16)

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        contenido = QWidget(); contenido.setStyleSheet("background: transparent;")
        form_lyt = QVBoxLayout(contenido)
        form_lyt.setContentsMargins(0, 0, 20, 0); form_lyt.setSpacing(14)

        estilo_grp = """
            QGroupBox { font-weight:bold; font-size:13px; border:1.5px solid #E0E3E8;
                border-radius:8px; margin-top:8px; padding-top:12px; background:#FFFFFF; }
            QGroupBox::title { subcontrol-origin:margin; left:12px; color:#4A5060; }
        """

        # ── Datos personales ─────────────────────────────────
        grp = QGroupBox("Datos personales"); grp.setStyleSheet(estilo_grp)
        g = QFormLayout(grp)
        g.setContentsMargins(16, 20, 16, 16); g.setSpacing(12)
        g.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.inp_nombre   = QLineEdit(); self.inp_nombre.setPlaceholderText("Nombre completo"); self.inp_nombre.setFixedHeight(36)
        self.inp_id       = QLineEdit(); self.inp_id.setPlaceholderText("Cédula o NIT"); self.inp_id.setFixedHeight(36)
        self.inp_telefono = QLineEdit(); self.inp_telefono.setPlaceholderText("Ej: 310 123 4567"); self.inp_telefono.setFixedHeight(36)
        self.inp_correo   = QLineEdit(); self.inp_correo.setPlaceholderText("correo@ejemplo.com"); self.inp_correo.setFixedHeight(36)

        # Fecha de nacimiento
        self.date_nacimiento = QDateEdit()
        self.date_nacimiento.setCalendarPopup(True)
        self.date_nacimiento.setDisplayFormat("dd / MM / yyyy")
        self.date_nacimiento.setFixedHeight(36)
        self.date_nacimiento.setDate(QDate(1990, 1, 1))
        self.date_nacimiento.setMaximumDate(QDate.currentDate())

        # Tipo de sangre
        self.cbo_sangre = QComboBox(); self.cbo_sangre.setFixedHeight(36)
        self.cbo_sangre.addItem("No especificado", None)
        for ts in TIPOS_SANGRE:
            self.cbo_sangre.addItem(ts, ts)

        # Rol
        self.cbo_rol = QComboBox(); self.cbo_rol.setFixedHeight(36)
        self._cargar_roles()

        g.addRow("Nombre completo *:", self.inp_nombre)
        g.addRow("Identificación *:", self.inp_id)
        g.addRow("Teléfono:", self.inp_telefono)
        g.addRow("Correo:", self.inp_correo)
        g.addRow("Fecha de nacimiento:", self.date_nacimiento)
        g.addRow("Tipo de sangre:", self.cbo_sangre)
        g.addRow("Rol:", self.cbo_rol)
        form_lyt.addWidget(grp)

        # ── Imagen cédula ─────────────────────────────────────
        grp_img = QGroupBox("Imagen de cédula (opcional)"); grp_img.setStyleSheet(estilo_grp)
        img_lyt = QVBoxLayout(grp_img)
        img_lyt.setContentsMargins(16, 20, 16, 16); img_lyt.setSpacing(10)
        fila_img = QHBoxLayout(); fila_img.setSpacing(12)
        self.lbl_preview = QLabel("Sin imagen\nseleccionada")
        self.lbl_preview.setFixedSize(130, 90); self.lbl_preview.setAlignment(Qt.AlignCenter)
        self.lbl_preview.setStyleSheet("background:#F4F5F7;border:1.5px dashed #C0C4D0;border-radius:6px;color:#9099A8;font-size:11px;")
        fila_img.addWidget(self.lbl_preview)
        col_img = QVBoxLayout(); col_img.setSpacing(8)
        self.lbl_nombre_img = QLabel("Ningún archivo seleccionado")
        self.lbl_nombre_img.setStyleSheet("color:#6B7080;font-size:12px;"); self.lbl_nombre_img.setWordWrap(True)
        col_img.addWidget(self.lbl_nombre_img)
        btn_sel = QPushButton("📎  Seleccionar imagen"); btn_sel.setObjectName("btn_secundario")
        btn_sel.setFixedHeight(34); btn_sel.setCursor(Qt.PointingHandCursor)
        btn_sel.clicked.connect(self._seleccionar_imagen)
        col_img.addWidget(btn_sel); col_img.addStretch()
        fila_img.addLayout(col_img, stretch=1); img_lyt.addLayout(fila_img)
        form_lyt.addWidget(grp_img)

        # ── Acceso al sistema ─────────────────────────────────
        grp_acc = QGroupBox("Acceso al sistema (opcional)"); grp_acc.setStyleSheet(estilo_grp)
        acc_lyt = QVBoxLayout(grp_acc)
        acc_lyt.setContentsMargins(16, 20, 16, 16); acc_lyt.setSpacing(12)
        self.chk_crear_usuario = QCheckBox("Crear usuario de acceso para esta persona")
        self.chk_crear_usuario.setStyleSheet("font-size:13px;")
        self.chk_crear_usuario.toggled.connect(lambda a: self.widget_acceso.setVisible(a))
        acc_lyt.addWidget(self.chk_crear_usuario)
        self.widget_acceso = QWidget(); self.widget_acceso.setVisible(False)
        wf = QFormLayout(self.widget_acceso)
        wf.setContentsMargins(0, 4, 0, 0); wf.setSpacing(12)
        wf.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.inp_usu = QLineEdit(); self.inp_usu.setPlaceholderText("Nombre de usuario"); self.inp_usu.setFixedHeight(36)
        self.inp_pw  = QLineEdit(); self.inp_pw.setPlaceholderText("Contraseña"); self.inp_pw.setEchoMode(QLineEdit.Password); self.inp_pw.setFixedHeight(36)
        self.inp_pw2 = QLineEdit(); self.inp_pw2.setPlaceholderText("Confirmar contraseña"); self.inp_pw2.setEchoMode(QLineEdit.Password); self.inp_pw2.setFixedHeight(36)
        wf.addRow("Usuario:", self.inp_usu); wf.addRow("Contraseña:", self.inp_pw); wf.addRow("Confirmar:", self.inp_pw2)
        acc_lyt.addWidget(self.widget_acceso); form_lyt.addWidget(grp_acc)

        self.lbl_msg = QLabel(""); self.lbl_msg.setWordWrap(True)
        self.lbl_msg.setStyleSheet("color:#8B1A1A;font-size:12px;")
        form_lyt.addWidget(self.lbl_msg); form_lyt.addStretch()
        scroll.setWidget(contenido); layout.addWidget(scroll, stretch=1)
        layout.addSpacing(12)

        fila_btns = QHBoxLayout(); fila_btns.setSpacing(12); fila_btns.addStretch()
        btn_cancelar = QPushButton("Cancelar"); btn_cancelar.setObjectName("btn_secundario")
        btn_cancelar.setFixedHeight(38); btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.clicked.connect(self.cancelado.emit); fila_btns.addWidget(btn_cancelar)
        btn_guardar = QPushButton("Guardar ✓"); btn_guardar.setObjectName("btn_primario")
        btn_guardar.setFixedHeight(38); btn_guardar.setMinimumWidth(140)
        btn_guardar.setCursor(Qt.PointingHandCursor); btn_guardar.clicked.connect(self._guardar)
        fila_btns.addWidget(btn_guardar); layout.addLayout(fila_btns)

    def _cargar_roles(self):
        self.cbo_rol.clear()
        for r in ModeloPersonal.listar_roles():
            self.cbo_rol.addItem(r["nombre_rol"], r["id_rol"])

    def _seleccionar_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Imagen de cédula", "",
            "Imágenes y PDF (*.png *.jpg *.jpeg *.bmp *.tiff *.pdf)")
        if not ruta: return
        self._ruta_imagen = ruta
        self.lbl_nombre_img.setText(os.path.basename(ruta))
        if ruta.lower().endswith((".png",".jpg",".jpeg",".bmp")):
            pix = QPixmap(ruta).scaled(130, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_preview.setPixmap(pix); self.lbl_preview.setText("")
        else:
            self.lbl_preview.setText("📄 PDF\nseleccionado")

    def _cargar_datos(self, id_personal: int):
        p = ModeloPersonal.obtener_por_id(id_personal)
        if not p: return
        self.inp_nombre.setText(p.get("nombre_completo",""))
        self.inp_id.setText(p.get("numero_id",""))
        self.inp_telefono.setText(p.get("telefono") or "")
        self.inp_correo.setText(p.get("correo") or "")

        fn = p.get("fecha_nacimiento")
        if fn:
            self.date_nacimiento.setDate(QDate(fn.year, fn.month, fn.day))

        ts = p.get("tipo_sangre")
        if ts:
            idx = self.cbo_sangre.findText(ts)
            if idx >= 0: self.cbo_sangre.setCurrentIndex(idx)

        id_rol = p.get("id_rol")
        for i in range(self.cbo_rol.count()):
            if self.cbo_rol.itemData(i) == id_rol:
                self.cbo_rol.setCurrentIndex(i); break

        ruta_img = p.get("ruta_imagen_cedula")
        if ruta_img and os.path.exists(ruta_img):
            self._ruta_imagen = ruta_img
            self.lbl_nombre_img.setText(os.path.basename(ruta_img))
            if ruta_img.lower().endswith((".png",".jpg",".jpeg",".bmp")):
                pix = QPixmap(ruta_img).scaled(130, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_preview.setPixmap(pix)



    def _parchar_date_edits(self):
        """Pone el ícono 📅 en el botón de todos los QDateEdit del formulario."""
        from PyQt5.QtWidgets import QDateEdit, QToolButton
        for de in self.findChildren(QDateEdit):
            de.setButtonSymbols(de.NoButtons)   # oculta flechas up/down nativas
            # El botón del calendario es el drop-down
            btn = de.findChild(QToolButton)
            if btn:
                btn.setText("📅")
                btn.setStyleSheet("""
                    QToolButton {
                        font-size: 14px;
                        border: none;
                        border-left: 1.5px solid #E0E3E8;
                        border-radius: 0px 7px 7px 0px;
                        background: #F4F5F7;
                        padding: 0px 6px;
                        color: #1A1C23;
                    }
                    QToolButton:hover {
                        background: #FEBC3D;
                    }
                """)

    def showEvent(self, event):
        """Parchar combos al mostrar el formulario (fix fondo negro Windows)."""
        super().showEvent(event)
        self._parchar_date_edits()
        from PyQt5.QtWidgets import QComboBox
        estilo = (
            "QAbstractItemView{background:#FFFFFF;color:#1A1C23;"
            "border:1.5px solid #D0D3DC;outline:0;padding:2px;}"
            "QAbstractItemView::item{background:#FFFFFF;color:#1A1C23;"
            "padding:8px 12px;min-height:30px;border:none;}"
            "QAbstractItemView::item:hover{background:#FFF8E6;color:#1A1C23;}"
            "QAbstractItemView::item:selected{background:#FEBC3D;"
            "color:#1A1C23;font-weight:bold;}"
        )
        for combo in self.findChildren(QComboBox):
            combo.view().setStyleSheet(estilo)

    def _guardar(self):
        nombre    = self.inp_nombre.text().strip()
        numero_id = self.inp_id.text().strip()
        telefono  = self.inp_telefono.text().strip()
        correo    = self.inp_correo.text().strip()
        id_rol    = self.cbo_rol.currentData()
        if not nombre or not numero_id:
            self.lbl_msg.setText("⚠  Los campos marcados con * son obligatorios.")
            return

        qd = self.date_nacimiento.date()
        fecha_nac = date(qd.year(), qd.month(), qd.day())
        tipo_sangre = self.cbo_sangre.currentData()

        ruta_guardada = None
        if self._ruta_imagen:
            try:
                os.makedirs(RUTA_CEDULAS, exist_ok=True)
                ext = os.path.splitext(self._ruta_imagen)[1]
                destino = os.path.join(RUTA_CEDULAS, f"{numero_id}{ext}")
                shutil.copy2(self._ruta_imagen, destino)
                ruta_guardada = destino
            except Exception as e:
                print(f"[Personal] Error imagen: {e}")

        if self.id_personal is None:
            id_nuevo = ModeloPersonal.crear(nombre, numero_id, telefono, correo,
                                            id_rol, ruta_guardada, fecha_nac, tipo_sangre)
            if id_nuevo == -1:
                self.lbl_msg.setText("⚠  Error al guardar. Identificación posiblemente duplicada.")
                return
            if self.chk_crear_usuario.isChecked():
                usu = self.inp_usu.text().strip(); pw = self.inp_pw.text(); pw2 = self.inp_pw2.text()
                if usu and pw:
                    if pw != pw2:
                        self.lbl_msg.setText("✅  Personal guardado, pero las contraseñas no coinciden.")
                        self.guardado.emit(); return
                    ModeloUsuario.crear(usu, pw, id_rol, id_nuevo)
        else:
            ok = ModeloPersonal.actualizar(self.id_personal, nombre, numero_id,
                                           telefono, correo, id_rol, ruta_guardada,
                                           fecha_nac, tipo_sangre)
            if not ok:
                self.lbl_msg.setText("⚠  Error al actualizar el registro.")
                return
        self.guardado.emit()


# ══════════════════════════════════════════════════════════════
# Panel de detalle
# ══════════════════════════════════════════════════════════════
class PanelDetalle(QFrame):

    solicitar_editar = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card { background:#FFFFFF; border:1.5px solid #E0E3E8; border-radius:10px; }
            QLabel { border:none; background:transparent; }
        """)
        self.setMinimumWidth(260)
        self._id_actual = None
        self._construir_ui()

    def _construir_ui(self):
        lyt = QVBoxLayout(self)
        lyt.setContentsMargins(20, 20, 20, 20); lyt.setSpacing(10)

        self.lbl_foto = QLabel("Sin imagen\nde cédula")
        self.lbl_foto.setFixedSize(170, 115); self.lbl_foto.setAlignment(Qt.AlignCenter)
        self.lbl_foto.setStyleSheet("background:#F4F5F7;border:1.5px dashed #C0C4D0 !important;border-radius:8px;color:#9099A8;font-size:11px;")
        lyt.addWidget(self.lbl_foto, alignment=Qt.AlignHCenter)

        # Nombre + badge cumpleaños
        fila_nombre = QHBoxLayout(); fila_nombre.setSpacing(6)
        self.lbl_nombre = QLabel("Selecciona una persona")
        self.lbl_nombre.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.lbl_nombre.setStyleSheet("color:#1A1C23;"); self.lbl_nombre.setWordWrap(True)
        self.lbl_nombre.setAlignment(Qt.AlignCenter)
        fila_nombre.addWidget(self.lbl_nombre, stretch=1)

        self.lbl_badge_cumple = QLabel("🎂")
        self.lbl_badge_cumple.setFixedSize(26, 26); self.lbl_badge_cumple.setAlignment(Qt.AlignCenter)
        self.lbl_badge_cumple.setStyleSheet("background-color:#FEBC3D;border-radius:13px;font-size:13px;")
        self.lbl_badge_cumple.setToolTip("¡Cumpleaños próximo!")
        self.lbl_badge_cumple.setVisible(False)
        fila_nombre.addWidget(self.lbl_badge_cumple)
        lyt.addLayout(fila_nombre)

        self.lbl_rol = QLabel("")
        self.lbl_rol.setAlignment(Qt.AlignCenter)
        self.lbl_rol.setStyleSheet("background:#FFF8D6;color:#8A6800;border-radius:8px;padding:3px 14px;font-size:11px;font-weight:bold;")
        lyt.addWidget(self.lbl_rol, alignment=Qt.AlignHCenter)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#E0E3E8;max-height:1px;"); lyt.addWidget(sep)

        self.campos: dict[str, QLabel] = {}
        for clave, etiqueta in [
            ("id_doc",    "📋  Identificación"),
            ("telefono",  "📞  Teléfono"),
            ("correo",    "✉   Correo"),
            ("nacimiento","🎂  Fecha de nacimiento"),
            ("sangre",    "🩸  Tipo de sangre"),
            ("registro",  "📅  Fecha de registro"),
        ]:
            lbl_et = QLabel(etiqueta); lbl_et.setStyleSheet("color:#6B7080;font-size:11px;")
            lyt.addWidget(lbl_et)
            lbl_val = QLabel("—"); lbl_val.setStyleSheet("color:#1A1C23;font-size:13px;font-weight:bold;")
            lbl_val.setWordWrap(True); lyt.addWidget(lbl_val)
            self.campos[clave] = lbl_val

        lyt.addStretch()
        self.btn_editar = QPushButton("✏  Editar registro"); self.btn_editar.setObjectName("btn_primario")
        self.btn_editar.setFixedHeight(36); self.btn_editar.setCursor(Qt.PointingHandCursor)
        self.btn_editar.setVisible(False)
        self.btn_editar.clicked.connect(lambda: self.solicitar_editar.emit(self._id_actual))
        lyt.addWidget(self.btn_editar)

    def mostrar(self, datos: dict):
        self._id_actual = datos.get("id_personal")

        # Foto
        ruta_img = datos.get("ruta_imagen_cedula")
        if ruta_img and os.path.exists(ruta_img):
            if ruta_img.lower().endswith((".png",".jpg",".jpeg",".bmp")):
                pix = QPixmap(ruta_img).scaled(170, 115, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.lbl_foto.setPixmap(pix); self.lbl_foto.setText("")
            else:
                self.lbl_foto.clear(); self.lbl_foto.setText("📄 Cédula PDF")
        else:
            self.lbl_foto.clear(); self.lbl_foto.setText("Sin imagen\nde cédula")

        self.lbl_nombre.setText(datos.get("nombre_completo","—"))
        self.lbl_rol.setText(datos.get("nombre_rol") or "Sin rol")

        # Fecha nacimiento + alerta cumpleaños
        fn   = datos.get("fecha_nacimiento")
        dias = ModeloPersonal.dias_para_cumpleanos(fn)
        if fn:
            fn_str = fn.strftime("%d / %m / %Y") if hasattr(fn,"strftime") else str(fn)
            if dias is not None and dias <= DIAS_ALERTA:
                sufijo = "¡Hoy! 🎂" if dias == 0 else f"⚠ Faltan {dias} día(s)"
                fn_str += f"   {sufijo}"
            self.campos["nacimiento"].setText(fn_str)
            self.lbl_badge_cumple.setVisible(dias is not None and dias <= DIAS_ALERTA)
        else:
            self.campos["nacimiento"].setText("—")
            self.lbl_badge_cumple.setVisible(False)

        self.campos["id_doc"].setText(datos.get("numero_id","—"))
        self.campos["telefono"].setText(datos.get("telefono") or "—")
        self.campos["correo"].setText(datos.get("correo") or "—")
        self.campos["sangre"].setText(datos.get("tipo_sangre") or "—")
        fr = datos.get("fecha_registro","")
        self.campos["registro"].setText(fr.strftime("%d/%m/%Y") if hasattr(fr,"strftime") else str(fr)[:10])
        self.btn_editar.setVisible(True)

    def limpiar(self):
        self._id_actual = None
        self.lbl_foto.clear(); self.lbl_foto.setText("Sin imagen\nde cédula")
        self.lbl_nombre.setText("Selecciona una persona")
        self.lbl_rol.setText(""); self.lbl_badge_cumple.setVisible(False)
        for lbl in self.campos.values(): lbl.setText("—")
        self.btn_editar.setVisible(False)


# ══════════════════════════════════════════════════════════════
# Tabla de personal
# ══════════════════════════════════════════════════════════════
class TablaPersonal(QWidget):

    solicitar_editar  = pyqtSignal(int)
    solicitar_agregar = pyqtSignal()
    ir_menu           = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._personal_data = []
        self._construir_ui()

    def _construir_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(12)
        enc = QHBoxLayout()
        btn_back = QPushButton("← Volver"); btn_back.setObjectName("btn_secundario")
        btn_back.setFixedHeight(32); btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.ir_menu.emit); enc.addWidget(btn_back)
        lbl = QLabel("Personal registrado"); lbl.setObjectName("titulo_modulo")
        lbl.setFont(QFont("Segoe UI", 20, QFont.Bold)); enc.addWidget(lbl, stretch=1)
        btn_nuevo = QPushButton("+ Agregar personal"); btn_nuevo.setObjectName("btn_primario")
        btn_nuevo.setFixedHeight(36); btn_nuevo.setCursor(Qt.PointingHandCursor)
        btn_nuevo.clicked.connect(self.solicitar_agregar.emit); enc.addWidget(btn_nuevo)
        layout.addLayout(enc)

        splitter = QSplitter(Qt.Horizontal); splitter.setHandleWidth(4)
        splitter.setStyleSheet("QSplitter::handle{background:#E0E3E8;}")

        self.tabla = QTableWidget(); self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Nombre completo","Identificación","Teléfono","Correo","Rol"
        ])
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setShowGrid(False); self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("QTableWidget{alternate-background-color:#F9FAFC;}")
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
            fn   = p.get("fecha_nacimiento")
            dias = ModeloPersonal.dias_para_cumpleanos(fn)
            alerta = dias is not None and dias <= DIAS_ALERTA

            # Nombre con icono de alerta si cumpleaños próximo
            nombre_txt = ("🎂 " if alerta else "") + p["nombre_completo"]
            item_nombre = QTableWidgetItem(nombre_txt)
            if alerta:
                item_nombre.setForeground(QColor("#8B1A1A"))
                tooltip = "¡Cumpleaños hoy!" if dias == 0 else f"¡Cumpleaños en {dias} día(s)!"
                item_nombre.setToolTip(tooltip)
            self.tabla.setItem(fila, 0, item_nombre)
            self.tabla.setItem(fila, 1, QTableWidgetItem(p["numero_id"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(p.get("telefono") or "—"))
            self.tabla.setItem(fila, 3, QTableWidgetItem(p.get("correo") or "—"))
            self.tabla.setItem(fila, 4, QTableWidgetItem(p.get("nombre_rol") or "—"))
            self.tabla.setRowHeight(fila, 56)
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

    refrescar_badge_personal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._pagina_editar = 3
        self._construir_ui()

    def _construir_ui(self):
        raiz = QVBoxLayout(self); raiz.setContentsMargins(32,28,32,28); raiz.setSpacing(0)
        lbl_mod = QLabel("Módulo de Personal"); lbl_mod.setObjectName("titulo_modulo")
        lbl_mod.setFont(QFont("Segoe UI", 22, QFont.Bold)); raiz.addWidget(lbl_mod)
        lbl_sub = QLabel("Gestión del equipo  ·  Selecciona una acción")
        lbl_sub.setObjectName("subtitulo_modulo"); raiz.addWidget(lbl_sub)
        raiz.addSpacing(16)

        self.stack = QStackedWidget(); raiz.addWidget(self.stack, stretch=1)
        self.stack.addWidget(self._crear_menu())

        self.form_reg = FormularioPersonal()
        self.form_reg.guardado.connect(self._tras_guardar)
        self.form_reg.cancelado.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.form_reg)

        self.tabla_personal = TablaPersonal()
        self.tabla_personal.solicitar_agregar.connect(self._abrir_registrar)
        self.tabla_personal.solicitar_editar.connect(self._abrir_editar)
        self.tabla_personal.ir_menu.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.addWidget(self.tabla_personal)
        self.stack.addWidget(QWidget())

    def _crear_menu(self) -> QWidget:
        pagina = QWidget(); pagina.setStyleSheet("background:transparent;")
        lyt = QVBoxLayout(pagina); lyt.setContentsMargins(0,0,0,0); lyt.setSpacing(16)

        lyt.addWidget(self._crear_card("👤","Registrar personal",
            "Agrega un nuevo miembro: datos personales, fecha de nacimiento,\ntipo de sangre, rol y acceso opcional al sistema.",
            "Registrar", self._abrir_registrar))

        # Card Ver personal con badge si hay cumpleaños próximos
        card_ver = self._crear_card("📋","Ver personal registrado",
            "Lista completa con panel de detalle individual\npara editar o consultar cada registro.",
            "Ver personal", self._ir_tabla)
        lyt.addWidget(card_ver)

        hay_cumple = ModeloPersonal.hay_cumpleanos_proximos(DIAS_ALERTA)
        if hay_cumple:
            badge_cumple = QLabel("🎂  Hay cumpleaños próximos (menos de 5 días)")
            badge_cumple.setStyleSheet("""
                background:#FFF8D6; color:#8A6800;
                border:1.5px solid #FEBC3D; border-radius:6px;
                padding:6px 14px; font-size:12px; font-weight:bold;
            """)
            lyt.addWidget(badge_cumple)

        lyt.addStretch()
        return pagina

    @staticmethod
    def _crear_card(icono, titulo, desc, txt_btn, accion) -> QFrame:
        card = QFrame(); card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card{background:#FFFFFF;border:1.5px solid #E0E3E8;border-radius:10px;}
            QFrame#card:hover{border-color:#FEBC3D;}
        """)
        lyt = QHBoxLayout(card); lyt.setContentsMargins(20,16,20,16); lyt.setSpacing(16)
        lbl_ico = QLabel(icono); lbl_ico.setFont(QFont("Arial",36))
        lbl_ico.setFixedSize(64,64); lbl_ico.setAlignment(Qt.AlignCenter)
        lbl_ico.setStyleSheet("background:#FFFBEA;border-radius:32px;"); lyt.addWidget(lbl_ico)
        col = QVBoxLayout(); col.setSpacing(4)
        lbl_tit = QLabel(titulo); lbl_tit.setFont(QFont("Segoe UI",14,QFont.Bold))
        lbl_tit.setStyleSheet("color:#1A1C23;"); col.addWidget(lbl_tit)
        lbl_desc = QLabel(desc); lbl_desc.setStyleSheet("color:#6B7080;font-size:12px;")
        lbl_desc.setWordWrap(True); col.addWidget(lbl_desc)
        fila_btn = QHBoxLayout()
        btn = QPushButton(txt_btn); btn.setObjectName("btn_secundario")
        btn.setFixedHeight(36); btn.setCursor(Qt.PointingHandCursor); btn.clicked.connect(accion)
        fila_btn.addWidget(btn); fila_btn.addStretch(); col.addLayout(fila_btn)
        lyt.addLayout(col, stretch=1); return card

    def _abrir_registrar(self):
        self.stack.removeWidget(self.form_reg); self.form_reg.deleteLater()
        self.form_reg = FormularioPersonal()
        self.form_reg.guardado.connect(self._tras_guardar)
        self.form_reg.cancelado.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.insertWidget(1, self.form_reg); self.stack.setCurrentIndex(1)

    def _ir_tabla(self):
        self.tabla_personal.actualizar()
        self.refrescar_badge_personal.emit(ModeloPersonal.hay_cumpleanos_proximos(DIAS_ALERTA))
        self.stack.setCurrentIndex(2)

    def _abrir_editar(self, id_personal: int):
        form = FormularioPersonal(id_personal=id_personal)
        form.guardado.connect(self._tras_guardar_edicion)
        form.cancelado.connect(lambda: self.stack.setCurrentIndex(2))
        old = self.stack.widget(self._pagina_editar)
        if old: self.stack.removeWidget(old); old.deleteLater()
        self.stack.insertWidget(self._pagina_editar, form)
        self.stack.setCurrentIndex(self._pagina_editar)

    def _tras_guardar(self):
        self.refrescar_badge_personal.emit(ModeloPersonal.hay_cumpleanos_proximos(DIAS_ALERTA))
        QMessageBox.information(self, "Guardado", "✅  Personal guardado correctamente.")
        self.stack.setCurrentIndex(0)

    def _tras_guardar_edicion(self):
        self.tabla_personal.actualizar()
        self.refrescar_badge_personal.emit(ModeloPersonal.hay_cumpleanos_proximos(DIAS_ALERTA))
        QMessageBox.information(self, "Actualizado", "✅  Registro actualizado correctamente.")
        self.stack.setCurrentIndex(2)
