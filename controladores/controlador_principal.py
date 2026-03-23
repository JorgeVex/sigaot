"""
============================================================
SIGAOT - Controlador Principal
Archivo: controladores/controlador_principal.py
Responsabilidad: gestiona la lógica de la ventana principal
                 y coordina los sub-controladores de módulo.
============================================================
"""

from PyQt5.QtCore import QObject, QTimer

from modelos.matricula import ModeloMatricula


class ControladorPrincipal(QObject):
    """
    Controlador de la ventana principal (shell + sidebar).
    También programa una verificación periódica de alertas
    de matrículas cada 30 minutos mientras la app esté abierta.
    """

    _INTERVALO_ALERTA_MS = 30 * 60 * 1000   # 30 minutos en ms

    def __init__(self, ventana, datos_usuario: dict):
        super().__init__()
        self.ventana       = ventana
        self.datos_usuario = datos_usuario

        # Temporizador para re-verificar alertas periódicamente
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._verificar_alertas)
        self._timer.start(self._INTERVALO_ALERTA_MS)

    # ── Alertas ──────────────────────────────────────────────

    def _verificar_alertas(self):
        """Actualiza el badge de matrículas según estado actual."""
        hay_alertas = ModeloMatricula.hay_proximas_a_vencer(30)
        self.ventana._actualizar_badge_alerta(hay_alertas)
