-- ============================================================
-- SIGAOT - Sistema Integrado de Gestión Administrativa y
--          Operativa de Transporte
-- Base de datos principal
-- Empresa: Trans-Alcayá
-- ============================================================

CREATE DATABASE IF NOT EXISTS sigaot
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_spanish_ci;

USE sigaot;

-- ------------------------------------------------------------
-- Tabla de roles del sistema
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id_rol        INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol    VARCHAR(50) NOT NULL UNIQUE,
    descripcion   VARCHAR(200),
    activo        TINYINT(1) DEFAULT 1,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Insertar roles base
INSERT INTO roles (nombre_rol, descripcion) VALUES
    ('Gerente',  'Acceso completo a todas las funciones del sistema'),
    ('Apoyo 1',  'Funciones de apoyo administrativo nivel 1'),
    ('Apoyo 2',  'Funciones de apoyo administrativo nivel 2'),
    ('Conductor','Acceso limitado para conductores');

-- ------------------------------------------------------------
-- Tabla de personal
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS personal (
    id_personal       INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo   VARCHAR(150) NOT NULL,
    numero_id         VARCHAR(30) NOT NULL UNIQUE,
    telefono          VARCHAR(20),
    correo            VARCHAR(100),
    ruta_imagen_cedula VARCHAR(300),
    id_rol            INT,
    activo            TINYINT(1) DEFAULT 1,
    fecha_registro    DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_personal_rol FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla de usuarios del sistema
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario    INT AUTO_INCREMENT PRIMARY KEY,
    usuario       VARCHAR(50) NOT NULL UNIQUE,
    contrasena    VARCHAR(255) NOT NULL,   -- Almacena hash SHA-256
    id_personal   INT,
    id_rol        INT NOT NULL,
    activo        TINYINT(1) DEFAULT 1,
    ultimo_acceso DATETIME,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuario_personal FOREIGN KEY (id_personal) REFERENCES personal(id_personal),
    CONSTRAINT fk_usuario_rol      FOREIGN KEY (id_rol)      REFERENCES roles(id_rol)
) ENGINE=InnoDB;

-- Usuario por defecto: Alicia / 123456
-- Contraseña hasheada con SHA-256: 8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92
INSERT INTO usuarios (usuario, contrasena, id_rol) VALUES
    ('Alicia', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 1);

-- ------------------------------------------------------------
-- Tabla de vehículos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vehiculos (
    id_vehiculo   INT AUTO_INCREMENT PRIMARY KEY,
    placa         VARCHAR(20) NOT NULL UNIQUE,
    propietario   VARCHAR(150) NOT NULL,
    conductor     VARCHAR(150) NOT NULL,
    tipo_vehiculo VARCHAR(50) NOT NULL,    -- camioneta / furgoneta
    habilitado    TINYINT(1) DEFAULT 1,   -- 0 = inhabilitado
    motivo_inhabilitacion VARCHAR(300),
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla de matrículas (vencimientos por vehículo)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS matriculas (
    id_matricula  INT AUTO_INCREMENT PRIMARY KEY,
    id_vehiculo   INT NOT NULL,
    tipo          ENUM(
                    'BIMENSUAL',
                    'SOAT',
                    'RTM',
                    'TO',
                    'RCC',
                    'RCE',
                    'POLIZA_TODO_RIESGO'
                  ) NOT NULL,
    fecha_vencimiento DATE,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_matricula_vehiculo FOREIGN KEY (id_vehiculo) REFERENCES vehiculos(id_vehiculo),
    CONSTRAINT uq_vehiculo_tipo UNIQUE (id_vehiculo, tipo)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Vista: vehículos con sus matrículas (útil para reportes)
-- ------------------------------------------------------------
CREATE OR REPLACE VIEW vista_vehiculos_matriculas AS
SELECT
    v.id_vehiculo,
    v.placa,
    v.propietario,
    v.conductor,
    v.tipo_vehiculo,
    v.habilitado,
    m.tipo        AS tipo_matricula,
    m.fecha_vencimiento,
    DATEDIFF(m.fecha_vencimiento, CURDATE()) AS dias_restantes
FROM vehiculos v
LEFT JOIN matriculas m ON v.id_vehiculo = m.id_vehiculo;

-- ============================================================
-- Fin del script
-- ============================================================
