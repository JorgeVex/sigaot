"""
============================================================
SIGAOT - Modelo de Vehículos
Archivo: modelos/vehiculo.py
Responsabilidad: acceso a datos de la tabla `vehiculos`
============================================================
"""

from base_datos.conexion import bd


class ModeloVehiculo:
    """Gestión CRUD de vehículos de la flota."""

    # ── Consultas ────────────────────────────────────────────

    @staticmethod
    def listar_todos() -> list:
        """Devuelve todos los vehículos registrados."""
        sql = """
            SELECT id_vehiculo, placa, propietario, conductor,
                   tipo_vehiculo, habilitado, fecha_registro
            FROM   vehiculos
            ORDER  BY placa
        """
        return bd.consultar(sql)

    @staticmethod
    def listar_habilitados() -> list:
        """Devuelve solo los vehículos activos/habilitados."""
        sql = """
            SELECT id_vehiculo, placa, propietario, conductor,
                   tipo_vehiculo
            FROM   vehiculos
            WHERE  habilitado = 1
            ORDER  BY placa
        """
        return bd.consultar(sql)

    @staticmethod
    def listar_inhabilitados() -> list:
        """Devuelve los vehículos inhabilitados."""
        sql = """
            SELECT id_vehiculo, placa, propietario, conductor,
                   tipo_vehiculo, motivo_inhabilitacion
            FROM   vehiculos
            WHERE  habilitado = 0
            ORDER  BY placa
        """
        return bd.consultar(sql)

    @staticmethod
    def obtener_por_id(id_vehiculo: int) -> dict | None:
        """Devuelve un vehículo por su PK."""
        sql = "SELECT * FROM vehiculos WHERE id_vehiculo = %s"
        resultado = bd.consultar(sql, (id_vehiculo,))
        return resultado[0] if resultado else None

    @staticmethod
    def obtener_por_placa(placa: str) -> dict | None:
        """Devuelve un vehículo buscando por placa."""
        sql = "SELECT * FROM vehiculos WHERE placa = %s"
        resultado = bd.consultar(sql, (placa.upper().strip(),))
        return resultado[0] if resultado else None

    # ── Creación ─────────────────────────────────────────────

    @staticmethod
    def crear(placa: str, propietario: str, conductor: str,
              tipo_vehiculo: str) -> int:
        """
        Inserta un vehículo nuevo.
        Devuelve el id generado o -1 si falla.
        """
        sql = """
            INSERT INTO vehiculos (placa, propietario, conductor, tipo_vehiculo)
            VALUES (%s, %s, %s, %s)
        """
        exito = bd.ejecutar(
            sql,
            (placa.upper().strip(), propietario.strip(),
             conductor.strip(), tipo_vehiculo.strip()),
        )
        return bd.ultima_id() if exito else -1

    # ── Actualización ────────────────────────────────────────

    @staticmethod
    def actualizar(id_vehiculo: int, placa: str, propietario: str,
                   conductor: str, tipo_vehiculo: str) -> bool:
        """Actualiza los datos de un vehículo existente."""
        sql = """
            UPDATE vehiculos
            SET    placa = %s, propietario = %s,
                   conductor = %s, tipo_vehiculo = %s
            WHERE  id_vehiculo = %s
        """
        return bd.ejecutar(
            sql,
            (placa.upper().strip(), propietario.strip(),
             conductor.strip(), tipo_vehiculo.strip(), id_vehiculo),
        )

    # ── Habilitación / inhabilitación ────────────────────────

    @staticmethod
    def inhabilitar(id_vehiculo: int, motivo: str = "") -> bool:
        """Marca un vehículo como inhabilitado."""
        sql = """
            UPDATE vehiculos
            SET    habilitado = 0, motivo_inhabilitacion = %s
            WHERE  id_vehiculo = %s
        """
        return bd.ejecutar(sql, (motivo.strip(), id_vehiculo))

    @staticmethod
    def habilitar(id_vehiculo: int) -> bool:
        """Reactiva un vehículo inhabilitado."""
        sql = """
            UPDATE vehiculos
            SET    habilitado = 1, motivo_inhabilitacion = NULL
            WHERE  id_vehiculo = %s
        """
        return bd.ejecutar(sql, (id_vehiculo,))
