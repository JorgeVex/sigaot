"""
============================================================
SIGAOT - Diálogo: Nueva fecha de vencimiento de matrícula
Archivo: vistas/dialogo_fecha.py

Modal OBLIGATORIO que aparece al subir un soporte de matrícula.
El usuario no puede cerrar sin confirmar una fecha válida.
============================================================
"""

from datetime import date
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDateEdit, QFrame,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont


class DialogoNuevaFecha(QDialog):
    """
    Diálogo modal que exige al usuario ingresar la nueva
    fecha de vencimiento de una matrícula al subir un soporte.

    No se puede cerrar con X ni con Escape sin haber
    confirmado la fecha.
    """

    def __init__(self, tipo: str, placa: str, parent=None):
        super().__init__(parent)
        self.tipo  = tipo
        self.placa = placa
        self._construir_ui()

        # Impedir cierre con X del sistema operativo
        self.setWindowFlags(
            Qt.Dialog |
            Qt.WindowTitleHint |
            Qt.CustomizeWindowHint   # quita el botón X
        )

    # ── Bloquear Escape ──────────────────────────────────────

    def keyPressEvent(self, event):
        """Impide cerrar el diálogo con la tecla Escape."""
        if event.key() == Qt.Key_Escape:
            return          # absorber evento, no hacer nada
        super().keyPressEvent(event)

    def reject(self):
        """Impide que el diálogo se cierre al hacer clic fuera."""
        pass                # sobrescrito intencionalmente

    # ── UI ───────────────────────────────────────────────────

    def _construir_ui(self):
        self.setWindowTitle("Nueva fecha de vencimiento")
        self.setFixedWidth(400)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # ── Ícono + título ───────────────────────────────────
        fila_tit = QHBoxLayout()
        fila_tit.setSpacing(10)

        lbl_ico = QLabel("📅")
        lbl_ico.setFont(QFont("Arial", 28))
        lbl_ico.setFixedWidth(44)
        lbl_ico.setAlignment(Qt.AlignVCenter)
        fila_tit.addWidget(lbl_ico)

        col_tit = QVBoxLayout()
        col_tit.setSpacing(2)

        lbl_titulo = QLabel("Fecha de vencimiento requerida")
        lbl_titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #1E2027;")
        col_tit.addWidget(lbl_titulo)

        lbl_sub = QLabel(
            f"Matrícula: <b>{self.tipo}</b>  ·  Vehículo: <b>{self.placa}</b>"
        )
        lbl_sub.setStyleSheet("color: #6B7080; font-size: 12px;")
        col_tit.addWidget(lbl_sub)

        fila_tit.addLayout(col_tit, stretch=1)
        layout.addLayout(fila_tit)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #E0E3E8;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        # ── Aviso ────────────────────────────────────────────
        lbl_aviso = QLabel(
            "⚠  Para registrar el soporte debes indicar la nueva\n"
            "      fecha de vencimiento de esta matrícula."
        )
        lbl_aviso.setStyleSheet("""
            background: #FFF8D6;
            border: 1.5px solid #F5C400;
            border-radius: 6px;
            padding: 10px 12px;
            color: #5C4400;
            font-size: 12px;
        """)
        lbl_aviso.setWordWrap(True)
        layout.addWidget(lbl_aviso)

        # ── Selector de fecha ────────────────────────────────
        lbl_campo = QLabel("Nueva fecha de vencimiento *")
        lbl_campo.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_campo.setStyleSheet("color: #4A5060;")
        layout.addWidget(lbl_campo)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd / MM / yyyy")
        self.date_edit.setFixedHeight(42)
        self.date_edit.setDate(QDate.currentDate().addMonths(12))
        self.date_edit.setMinimumDate(QDate.currentDate().addDays(1))
        self.date_edit.setStyleSheet("""
            QDateEdit {
                border: 2px solid #F5C400;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 15px;
                font-weight: bold;
                color: #1E2027;
                background: #FFFDF0;
            }
            QDateEdit:focus { border-color: #D4A900; }
        """)
        layout.addWidget(self.date_edit)

        # Mensaje de error (oculto por defecto)
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet(
            "color: #E74C3C; font-size: 12px; padding-left: 2px;"
        )
        self.lbl_error.setVisible(False)
        layout.addWidget(self.lbl_error)

        layout.addSpacing(4)

        # ── Botones ──────────────────────────────────────────
        fila_btns = QHBoxLayout()
        fila_btns.setSpacing(12)
        fila_btns.addStretch()

        btn_cancelar = QPushButton("Cancelar soporte")
        btn_cancelar.setFixedHeight(38)
        btn_cancelar.setMinimumWidth(140)
        btn_cancelar.setCursor(Qt.PointingHandCursor)
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1.5px solid #C0C4D0;
                border-radius: 6px;
                color: #1E2027;
                font-size: 13px;
                padding: 0 16px;
            }
            QPushButton:hover {
                border-color: #E74C3C;
                color: #E74C3C;
            }
        """)
        # Este botón SÍ cierra el diálogo como "Rejected"
        btn_cancelar.clicked.connect(self._cancelar)
        fila_btns.addWidget(btn_cancelar)

        btn_confirmar = QPushButton("✓  Confirmar fecha")
        btn_confirmar.setFixedHeight(38)
        btn_confirmar.setMinimumWidth(160)
        btn_confirmar.setCursor(Qt.PointingHandCursor)
        btn_confirmar.setStyleSheet("""
            QPushButton {
                background: #F5C400;
                border: none;
                border-radius: 6px;
                color: #1E2027;
                font-size: 13px;
                font-weight: bold;
                padding: 0 16px;
            }
            QPushButton:hover { background: #D4A900; }
            QPushButton:pressed { background: #B89200; }
        """)
        btn_confirmar.clicked.connect(self._confirmar)
        fila_btns.addWidget(btn_confirmar)

        layout.addLayout(fila_btns)

    # ── Acciones ─────────────────────────────────────────────

    def _confirmar(self):
        """Valida que la fecha sea futura y acepta el diálogo."""
        qd = self.date_edit.date()
        fecha_sel = date(qd.year(), qd.month(), qd.day())

        if fecha_sel <= date.today():
            self.lbl_error.setText(
                "⚠  La nueva fecha debe ser posterior a hoy."
            )
            self.lbl_error.setVisible(True)
            return

        self.lbl_error.setVisible(False)
        self.accept()   # QDialog.Accepted

    def _cancelar(self):
        """Cierra el diálogo como Rejected (cancela la operación)."""
        # Llamamos al accept de QDialog directamente con código Rejected
        QDialog.reject(self)

    # ── Getter ───────────────────────────────────────────────

    def obtener_fecha(self) -> date:
        """Devuelve la fecha confirmada como objeto datetime.date."""
        qd = self.date_edit.date()
        return date(qd.year(), qd.month(), qd.day())
