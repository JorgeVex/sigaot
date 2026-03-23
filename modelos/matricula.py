"""
============================================================
SIGAOT - Modelo de Matrículas
Archivo: modelos/matricula.py
Responsabilidad: acceso a datos de la tabla `matriculas`
============================================================
"""

from datetime import date, datetime
from base_datos.conexion import bd


# Tipos de matrícula admitidos en el sistema
TIPOS_MATRICULA = [
    "BIMENSUAL",
    "SOAT",
    "RTM",
    "TO",
    "RCC",
    "RCE",
    "POLIZA_TODO_RIESGO",
]

# Etiqueta visual para cada tipo (se muestra en la UI)
ETIQUETAS_MATRICULA = {
    "BIMENSUAL":        "Bimensual",
    "SOAT":             "SOAT",
    "RTM":              "RTM",
    "TO":               "TO",
    "RCC":              "RCC",
    "RCE":              "RCE",
    "POLIZA_TODO_RIESGO": "Póliza todo riesgo",
}


class ModeloMatricula:
    """Gestión de fechas de vencimiento de matrículas."""

    # ── Consultas ────────────────────────────────────────────

    @staticmethod
    def obtener_por_vehiculo(id_vehiculo: int) -> list:
        """Devuelve todas las matrículas de un vehículo."""
        sql = """
            SELECT id_matricula, id_vehiculo, tipo,
                   fecha_vencimiento, fecha_actualizacion
            FROM   matriculas
            WHERE  id_vehiculo = %s
            ORDER  BY FIELD(tipo,
                'BIMENSUAL','SOAT','RTM','TO',
                'RCC','RCE','POLIZA_TODO_RIESGO')
        """
        return bd.consultar(sql, (id_vehiculo,))

    @staticmethod
    def obtener_todas_con_placa() -> list:
        """
        Devuelve todas las matrículas con la placa del vehículo.
        Útil para el panel de alertas global.
        """
        sql = """
            SELECT m.id_matricula, v.placa, m.tipo,
                   m.fecha_vencimiento,
                   DATEDIFF(m.fecha_vencimiento, CURDATE()) AS dias_restantes
            FROM   matriculas m
            JOIN   vehiculos v ON v.id_vehiculo = m.id_vehiculo
            WHERE  v.habilitado = 1
              AND  m.fecha_vencimiento IS NOT NULL
            ORDER  BY dias_restantes ASC
        """
        return bd.consultar(sql)

    @staticmethod
    def hay_proximas_a_vencer(dias_limite: int = 30) -> bool:
        """
        Comprueba si existe al menos una matrícula que vence
        en los próximos `dias_limite` días.
        """
        sql = """
            SELECT COUNT(*) AS total
            FROM   matriculas m
            JOIN   vehiculos v ON v.id_vehiculo = m.id_vehiculo
            WHERE  v.habilitado = 1
              AND  m.fecha_vencimiento IS NOT NULL
              AND  DATEDIFF(m.fecha_vencimiento, CURDATE()) <= %s
              AND  DATEDIFF(m.fecha_vencimiento, CURDATE()) >= 0
        """
        resultado = bd.consultar(sql, (dias_limite,))
        return bool(resultado and resultado[0]["total"] > 0)

    # ── Guardado (insertar o actualizar) ─────────────────────

    @staticmethod
    def guardar(id_vehiculo: int, tipo: str,
                fecha_vencimiento: date) -> bool:
        """
        Inserta la matrícula si no existe; la actualiza si ya existe
        (INSERT … ON DUPLICATE KEY UPDATE).
        """
        if tipo not in TIPOS_MATRICULA:
            print(f"[Matrícula] Tipo desconocido: {tipo}")
            return False

        # Convertir date/datetime a string YYYY-MM-DD
        if isinstance(fecha_vencimiento, datetime):
            fecha_str = fecha_vencimiento.strftime("%Y-%m-%d")
        elif isinstance(fecha_vencimiento, date):
            fecha_str = fecha_vencimiento.isoformat()
        else:
            fecha_str = str(fecha_vencimiento)

        sql = """
            INSERT INTO matriculas (id_vehiculo, tipo, fecha_vencimiento)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                fecha_vencimiento   = VALUES(fecha_vencimiento),
                fecha_actualizacion = NOW()
        """
        return bd.ejecutar(sql, (id_vehiculo, tipo, fecha_str))

    @staticmethod
    def guardar_todas(id_vehiculo: int,
                      fechas: dict) -> bool:
        """
        Guarda en bloque un diccionario {tipo: fecha} para un vehículo.
        Devuelve True si todas se guardaron correctamente.
        """
        exito = True
        for tipo, fecha in fechas.items():
            if fecha is not None:
                ok = ModeloMatricula.guardar(id_vehiculo, tipo, fecha)
                if not ok:
                    exito = False
        return exito

    # ── Cálculo de estado / color ────────────────────────────

    @staticmethod
    def calcular_estado(fecha_vencimiento) -> str:
        """
        Devuelve una clave de estado según los días restantes:
          'vencida'     → ya venció
          'critica'     → < 7 días
          'urgente'     → 7-14 días
          'advertencia' → 15-30 días
          'proxima'     → 31-60 días
          'normal'      → > 60 días
          'sin_fecha'   → sin fecha registrada
        """
        if fecha_vencimiento is None:
            return "sin_fecha"

        hoy = date.today()
        if isinstance(fecha_vencimiento, str):
            fecha_vencimiento = datetime.strptime(
                fecha_vencimiento, "%Y-%m-%d"
            ).date()

        dias = (fecha_vencimiento - hoy).days

        if dias < 0:
            return "vencida"
        if dias < 7:
            return "critica"
        if dias < 15:
            return "urgente"
        if dias < 30:
            return "advertencia"
        if dias < 60:
            return "proxima"
        return "normal"
