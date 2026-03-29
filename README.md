# SIGAOT – Sistema Integrado de Gestión Administrativa y Operativa de Transporte
**Empresa:** Trans-Alcayá  
**Versión:** 1.0.0  
**Lenguaje:** Python 3.10+  
**Librería UI:** PyQt5  
**Base de datos:** MySQL (compatible con MySQL Workbench)

---

## 📁 Estructura del proyecto

```
SIGAOT/
├── main.py                        ← Punto de entrada
├── README.md
│
├── base_datos/
│   ├── __init__.py
│   └── conexion.py                ← Conexión MySQL (Singleton)
│
├── modelos/
│   ├── __init__.py
│   ├── usuario.py
│   ├── vehiculo.py
│   ├── matricula.py
│   └── personal.py
│
├── vistas/
│   ├── __init__.py
│   ├── vista_login.py
│   ├── vista_principal.py
│   ├── vista_inicio.py
│   ├── vista_vehiculos.py
│   └── vista_matriculas.py
│
├── controladores/
│   ├── __init__.py
│   ├── controlador_login.py
│   └── controlador_principal.py
│
├── recursos/
│   ├── estilos/
│   │   └── estilo.qss             
│   └── IMG/                       
│       ├── logo.png             
│       └── user.png             
│
└── SQL/
    └── sigaot_bd.sql            
```

---

## 🚀 Instalación y configuración

### 1. Requisitos previos

- Python 3.10 o superior
- MySQL Server 8.0+ (o MariaDB 10.6+)
- MySQL Workbench (recomendado)

### 2. Instalar dependencias Python

```bash
pip install PyQt5 mysql-connector-python
```

### 3. Crear la base de datos

1. Abre **MySQL Workbench**.
2. Conecta a tu servidor local.
3. Ve a **File → Open SQL Script** y abre `SQL/sigaot_bd.sql`.
4. Ejecuta el script completo (▶ o Ctrl+Shift+Enter).
5. Refresca la lista de schemas — debe aparecer **sigaot**.

### 4. Configurar credenciales de BD

Edita el archivo `base_datos/conexion.py` y ajusta los valores:

```python
_CONFIG_BD = {
    "host":     "localhost",
    "port":     3306,
    "user":     "root",       # ← tu usuario MySQL
    "password": "root",       # ← tu contraseña MySQL
    "database": "sigaot",
}
```

### 5. Agregar imágenes

Coloca tus imágenes en `recursos/IMG/`:

| Archivo       | Descripción                            | Tamaño sugerido |
|---------------|----------------------------------------|-----------------|
| `logo.png`    | Logo circular de Trans-Alcayá          | 200×200 px      |
| `user.png`    | Ícono de usuario (perfil genérico)     | 64×64 px        |

> Si no colocas las imágenes, la aplicación funciona igualmente  
> mostrando emojis de reemplazo (🚚, 👤).

### 6. Ejecutar la aplicación

```bash
cd SIGAOT
python main.py
```

---

## 🔐 Acceso inicial

| Campo       | Valor    |
|-------------|----------|
| Usuario     | `Alicia` |
| Contraseña  | `123456` |

---

## 🗺 Módulos disponibles

### Inicio
Pantalla de bienvenida con resumen de los módulos del sistema.

### Vehículos
- **Registrar vehículo:** placa, propietario, conductor, tipo (camioneta/furgoneta) y fechas de vencimiento de matrículas.
- **Editar vehículo:** modifica todos los datos excepto la placa.
- **Lista de vehículos:** tabla con estado, botones editar / inhabilitar / habilitar.
- **Inhabilitación:** registra el motivo y oculta el vehículo del servicio activo.

### Matrículas
Tipos gestionados: **BIMENSUAL, SOAT, RTM, TO, RCC, RCE, Póliza todo riesgo**.

**Sistema de colores (psicología del color):**

| Color           | Significado                    |
|-----------------|-------------------------------|
| ⬜ Blanco        | Vigente (más de 60 días)       |
| 🟢 Verde claro   | Próxima a vencer (1-2 meses)   |
| 🟡 Amarillo      | Menos de 30 días               |
| 🟠 Naranja       | Menos de 15 días               |
| 🔴 Rojo claro    | Menos de 7 días (¡urgente!)    |
| 🔴 Rojo oscuro   | Vencida                        |

**Alertas múltiples:**
1. **Notificación emergente** al iniciar sesión si hay vencimientos ≤ 30 días.
2. **Badge rojo (!)** sobre el ítem "Matrículas" del sidebar.
3. **Re-verificación automática** cada 30 minutos sin cerrar la app.

---

## 🏗 Arquitectura

```
Vista  ←──señales──→  Controlador  ←──llama──→  Modelo  ←──SQL──→  MySQL
(PyQt5 Widgets)       (QObject)                 (Clases)            (BD)
```

- **MVC estricto:** las vistas no acceden nunca directamente a la BD.
- **Singleton de conexión:** una sola instancia de `ConexionBD` durante toda la sesión.
- **Paradigma OOP:** cada capa es una clase con responsabilidades definidas.
- **Documentación en español:** todos los módulos, clases y métodos están comentados en español.

---

## 🔧 Solución de problemas frecuentes

| Error                                | Solución                                          |
|--------------------------------------|---------------------------------------------------|
| `mysql.connector.errors.ProgrammingError` | Verifica usuario/contraseña en `conexion.py` |
| `Unknown database 'sigaot'`          | Ejecuta el script SQL en MySQL Workbench          |
| La ventana aparece sin estilos       | Verifica que `recursos/estilos/estilo.qss` existe |
| No aparece el logo                   | Coloca `logo.png` en `recursos/IMG/`              |

---

© 2025 Trans-Alcayá. Todos los derechos reservados.
