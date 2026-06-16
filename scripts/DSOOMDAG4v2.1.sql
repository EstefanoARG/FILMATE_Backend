-- ====================================================================
-- 1. CONFIGURACIÓN INICIAL Y CREACIÓN
-- ====================================================================
DROP DATABASE IF EXISTS filmate_db;
CREATE DATABASE filmate_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE filmate_db;

-- ====================================================================
-- 2. ELIMINACIÓN DE TABLAS (Orden inverso estricto para evitar conflictos FK)
-- ====================================================================
DROP TABLE IF EXISTS log_actividad_sistema;
DROP TABLE IF EXISTS roles_permisos;
DROP TABLE IF EXISTS permisos;
DROP TABLE IF EXISTS usuarios_roles;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS log_validaciones_qr;
DROP TABLE IF EXISTS detalle_boleta_asientos;
DROP TABLE IF EXISTS detalle_boleta_confiteria;
DROP TABLE IF EXISTS boletas_tickets;
DROP TABLE IF EXISTS solicitudes_reembolso;
DROP TABLE IF EXISTS transacciones;
DROP TABLE IF EXISTS carrito_confiteria;
DROP TABLE IF EXISTS productos_confiteria;
DROP TABLE IF EXISTS categorias_confiteria;
DROP TABLE IF EXISTS bloqueos_temporales;
DROP TABLE IF EXISTS asientos_funciones;
DROP TABLE IF EXISTS asientos;
DROP TABLE IF EXISTS funciones;
DROP TABLE IF EXISTS salas;
DROP TABLE IF EXISTS cines;
DROP TABLE IF EXISTS colecciones_peliculas;
DROP TABLE IF EXISTS colecciones;
DROP TABLE IF EXISTS interacciones_peliculas;
DROP TABLE IF EXISTS resenas;
DROP TABLE IF EXISTS peliculas_generos;
DROP TABLE IF EXISTS generos;
DROP TABLE IF EXISTS peliculas;
DROP TABLE IF EXISTS seguidores;
DROP TABLE IF EXISTS historial_actividad;
DROP TABLE IF EXISTS tipos_documento;
DROP TABLE IF EXISTS usuarios;

-- ====================================================================
-- 3. ESTRUCTURA DE TABLAS MAESTRAS E INTERMEDIAS (DDL COMPLETAMENTE LIMPIO)
-- ====================================================================

-- --- MÓDULO: SEGURIDAD, ROLES Y PERMISOS (RBAC) ---

CREATE TABLE tipos_documento (
    id_tipo_doc INT AUTO_INCREMENT PRIMARY KEY,
    siglas VARCHAR(10) NOT NULL UNIQUE,     -- 'DNI', 'CE', 'PASAPORTE'
    descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE roles (
    id_role INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE, -- 'ADMINISTRADOR', 'CLIENTE'
    descripcion TEXT
);

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,           -- "Full name"
    username VARCHAR(50) NOT NULL UNIQUE,   -- "Username"
    correo VARCHAR(150) NOT NULL UNIQUE,    -- "Email"
    contrasena VARCHAR(255) NOT NULL,       -- "Password"
    id_tipo_doc INT NOT NULL DEFAULT 1,     -- Vinculado a DNI por defecto
    numero_documento VARCHAR(20) NOT NULL,  -- Número de identidad unívoco
    telefono VARCHAR(20) DEFAULT NULL,      -- "Phone number"
    url_perfil VARCHAR(255) DEFAULT 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_1', -- Foto para las reseñas
    estado_usuario VARCHAR(20) NOT NULL DEFAULT 'ACTIVO', -- 'ACTIVO', 'INACTIVO'
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_conexion TIMESTAMP DEFAULT NULL, -- Alimenta la grilla de control de accesos
    eliminado BOOLEAN NOT NULL DEFAULT FALSE, -- Control de Soft Delete
    fecha_eliminacion DATETIME DEFAULT NULL,  -- Auditoría temporal de baja física
    FOREIGN KEY (id_tipo_doc) REFERENCES tipos_documento(id_tipo_doc) ON DELETE RESTRICT,
    CONSTRAINT uq_documento_identidad UNIQUE (id_tipo_doc, numero_documento)
);

CREATE TABLE usuarios_roles (
    id_usuario INT,
    id_role INT,
    PRIMARY KEY (id_usuario, id_role),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_role) REFERENCES roles(id_role) ON DELETE CASCADE
);

CREATE TABLE permisos (
    id_permiso INT AUTO_INCREMENT PRIMARY KEY,
    codigo_permiso VARCHAR(50) NOT NULL UNIQUE, -- Ej: 'VER_HISTORIAL_TXN', 'CONFIG_PRECIOS'
    descripcion VARCHAR(150) NOT NULL,          -- Texto de la interfaz gráfica
    modulo VARCHAR(50) NOT NULL                 -- Agrupador visual: 'VENTA Y TICKETS', etc.
);

CREATE TABLE roles_permisos (
    id_role INT,
    id_permiso INT,
    PRIMARY KEY (id_role, id_permiso),
    FOREIGN KEY (id_role) REFERENCES roles(id_role) ON DELETE CASCADE,
    FOREIGN KEY (id_permiso) REFERENCES permisos(id_permiso) ON DELETE CASCADE
);


-- --- MÓDULO: PELÍCULAS Y ECOSYSTEMA SOCIAL (ESTILO LETTERBOXD / TMDb) ---

CREATE TABLE generos (
    id_genero INT PRIMARY KEY, -- Mantiene los IDs oficiales de la API de TMDb
    nombre_genero VARCHAR(50) NOT NULL
);

CREATE TABLE peliculas (
    id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    anio_lanzamiento INT NOT NULL,
    duracion_minutos INT NOT NULL,
    clasificacion VARCHAR(10) NOT NULL,    -- Ej: "+14", "APT", "PG-13"
    estado_pelicula VARCHAR(30) NOT NULL DEFAULT 'PRÓXIMAMENTE', -- 'ACTIVO', 'PRÓXIMAMENTE', 'EN CARTELERA'
    url_poster VARCHAR(255) NOT NULL,
    url_banner VARCHAR(255),
    url_trailer VARCHAR(255),
    sinopsis TEXT,
    elenco TEXT,
    director VARCHAR(150) NOT NULL,
    total_vistas_comunidad INT DEFAULT 0,
    total_favoritos_comunidad INT DEFAULT 0,
    eliminado BOOLEAN NOT NULL DEFAULT FALSE, -- Control de Soft Delete
    fecha_eliminacion DATETIME DEFAULT NULL   -- Auditoría temporal de baja física
);
CREATE TABLE peliculas_generos (
    id_pelicula INT,
    id_genero INT,
    PRIMARY KEY (id_pelicula, id_genero),
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_genero) REFERENCES generos(id_genero) ON DELETE CASCADE
);

CREATE TABLE resenas (
    id_resena INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_pelicula INT,
    puntuacion_estrellas INT DEFAULT NULL CHECK (puntuacion_estrellas BETWEEN 1 AND 5),
    comentario TEXT,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE
);

CREATE TABLE interacciones_peliculas (
    id_usuario INT,
    id_pelicula INT,
    vista BOOLEAN DEFAULT FALSE,
    favorita BOOLEAN DEFAULT FALSE,
    en_lista_seguimiento BOOLEAN DEFAULT FALSE,
    fecha_favorito TIMESTAMP DEFAULT NULL,
    PRIMARY KEY (id_usuario, id_pelicula),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE
);

CREATE TABLE colecciones (
    id_coleccion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    titulo_coleccion VARCHAR(150) NOT NULL,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    eliminado BOOLEAN NOT NULL DEFAULT FALSE, -- Control de Soft Delete
    fecha_eliminacion DATETIME DEFAULT NULL,  -- Auditoría temporal de baja física
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE colecciones_peliculas (
    id_coleccion INT,
    id_pelicula INT,
    PRIMARY KEY (id_coleccion, id_pelicula),
    FOREIGN KEY (id_coleccion) REFERENCES colecciones(id_coleccion) ON DELETE CASCADE,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE RESTRICT
);



CREATE TABLE seguidores (
    id_seguidor INT,  -- Usuario que sigue
    id_seguido INT,   -- Usuario que es seguido
    fecha_seguimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_seguidor, id_seguido),
    FOREIGN KEY (id_seguidor) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_seguido) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);


-- --- MÓDULO: INFRAESTRUCTURA DE CINES Y PLANIFICACIÓN DE CARTELERA ---

CREATE TABLE cines (
    id_cine INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cine VARCHAR(100) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    horarios_apertura VARCHAR(100),
    url_mapa_embebido TEXT DEFAULT NULL, -- URL para cargar el mapa interactivo nativo
    estado_cine VARCHAR(30) NOT NULL DEFAULT 'Activo', -- 'Activo', 'No operativo', 'Próximamente'
    observaciones TEXT DEFAULT NULL,
    eliminado BOOLEAN NOT NULL DEFAULT FALSE, -- Control de Soft Delete
    fecha_eliminacion DATETIME DEFAULT NULL   -- Auditoría temporal de baja física
);
CREATE TABLE salas (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    id_cine INT,
    nombre_sala VARCHAR(50) NOT NULL,
    tipo_sala VARCHAR(20) NOT NULL DEFAULT 'Stand.', -- 'Stand.', 'IMAX', '4DX', 'VIP'	
    tipo_formato VARCHAR(20) NOT NULL,                -- '2D', '3D'
    capacidad_asientos INT NOT NULL DEFAULT 0,
    estado_sala VARCHAR(20) NOT NULL DEFAULT 'Activa', -- 'Activa', 'Inactiva'
    eliminado BOOLEAN NOT NULL DEFAULT FALSE, -- Control de Soft Delete
    fecha_eliminacion DATETIME DEFAULT NULL,  -- Auditoría temporal de baja física
    FOREIGN KEY (id_cine) REFERENCES cines(id_cine) ON DELETE CASCADE
);

CREATE TABLE funciones (
    id_funcion INT AUTO_INCREMENT PRIMARY KEY,
    id_pelicula INT,
    id_sala INT,
    fecha_hora DATETIME NOT NULL,
    precio_base DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE RESTRICT,
    FOREIGN KEY (id_sala) REFERENCES salas(id_sala) ON DELETE CASCADE
);

CREATE TABLE asientos (
    id_asiento INT AUTO_INCREMENT PRIMARY KEY,
    id_sala INT,
    fila VARCHAR(5) NOT NULL,
    columna INT NOT NULL,
    tipo_asiento VARCHAR(20) DEFAULT 'Regular',       -- Ej: 'Regular', 'VIP', 'Discapacitado'
    estado_asiento VARCHAR(20) NOT NULL DEFAULT 'Activo', -- 'Activo', 'Inactiva' (Para pasillos/bloqueos)
    eliminado BOOLEAN NOT NULL DEFAULT FALSE, -- Control de Soft Delete
    fecha_eliminacion DATETIME DEFAULT NULL,  -- Auditoría temporal de baja física
    FOREIGN KEY (id_sala) REFERENCES salas(id_sala) ON DELETE CASCADE
);


-- --- MÓDULO: SELECCIÓN DE BUTACAS EN TIEMPO REAL ---

CREATE TABLE asientos_funciones (
    id_funcion INT,
    id_asiento INT,
    estado VARCHAR(20) DEFAULT 'Disponible', -- 'Disponible', 'Ocupado', 'Bloqueado'
    PRIMARY KEY (id_funcion, id_asiento),
    FOREIGN KEY (id_funcion) REFERENCES funciones(id_funcion) ON DELETE CASCADE,
    FOREIGN KEY (id_asiento) REFERENCES asientos(id_asiento) ON DELETE CASCADE
);

CREATE TABLE bloqueos_temporales (
    id_bloqueo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_funcion INT,
    id_asiento INT,
    fecha_bloqueo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expira_en TIMESTAMP NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_funcion, id_asiento) REFERENCES asientos_funciones(id_funcion, id_asiento) ON DELETE CASCADE
);


-- --- MÓDULO: CONFITERÍA / DULCERÍA ---

CREATE TABLE categorias_confiteria (
    id_categoria_confi INT AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(50) NOT NULL
);

CREATE TABLE productos_confiteria (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria_confi INT,
    nombre_producto VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    url_imagen VARCHAR(255) NOT NULL DEFAULT 'default_snack.png',
    stock INT NOT NULL DEFAULT 0,
    FOREIGN KEY (id_categoria_confi) REFERENCES categorias_confiteria(id_categoria_confi) ON DELETE SET NULL
);

CREATE TABLE carrito_confiteria (
    id_carrito INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_producto INT,
    cantidad INT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos_confiteria(id_producto) ON DELETE CASCADE
);


-- --- MÓDULO: PROCESAMIENTO TRANSACCIONAL Y EXPEDIENTES ADMINISTRATIVOS ---

CREATE TABLE transacciones (
    id_transaccion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_funcion INT,
    monto_boletos DECIMAL(10,2) NOT NULL,
    monto_confiteria DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    monto_total DECIMAL(10,2) NOT NULL,
    estado_pago VARCHAR(20) DEFAULT 'Pendiente', -- 'Pendiente', 'Aprobado', 'Fallido', 'Reembolsada'
    metodo_pago VARCHAR(50),                     -- Ej: 'Visa ****4521'
    fecha_transaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (id_funcion) REFERENCES funciones(id_funcion) ON DELETE RESTRICT
);

CREATE TABLE detalle_boleta_asientos (
    id_detalle_asiento INT AUTO_INCREMENT PRIMARY KEY,
    id_transaccion INT,
    id_asiento INT,
    ingresado BOOLEAN DEFAULT FALSE,         -- Control de acceso móvil (QR)
    fecha_ingreso TIMESTAMP DEFAULT NULL,
    FOREIGN KEY (id_transaccion) REFERENCES transacciones(id_transaccion) ON DELETE CASCADE,
    FOREIGN KEY (id_asiento) REFERENCES asientos(id_asiento) ON DELETE RESTRICT
);

CREATE TABLE detalle_boleta_confiteria (
    id_detalle_confi INT AUTO_INCREMENT PRIMARY KEY,
    id_transaccion INT,
    id_producto INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_transaccion) REFERENCES transacciones(id_transaccion) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos_confiteria(id_producto) ON DELETE RESTRICT
);

CREATE TABLE boletas_tickets (
    id_ticket INT AUTO_INCREMENT PRIMARY KEY,
    id_transaccion INT,
    codigo_qr_token VARCHAR(255) NOT NULL UNIQUE, -- Almacena el ID plano del QR
    estado_ticket VARCHAR(20) DEFAULT 'Valido',   -- 'Valido', 'Canjeado', 'Cancelado'
    fecha_emision TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_transaccion) REFERENCES transacciones(id_transaccion) ON DELETE CASCADE
);

CREATE TABLE solicitudes_reembolso (
    id_reembolso INT AUTO_INCREMENT PRIMARY KEY,
    id_transaccion INT,
    motivo TEXT NOT NULL,
    tipo_reembolso VARCHAR(30) NOT NULL DEFAULT 'Reembolso total',
    monto_reembolsado DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    estado_solicitud VARCHAR(20) DEFAULT 'Evaluacion',             
    comentario_administrador TEXT DEFAULT NULL,                    
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP NULL DEFAULT NULL, 
    FOREIGN KEY (id_transaccion) REFERENCES transacciones(id_transaccion) ON DELETE CASCADE
);


-- --- MÓDULO: AUDITORÍA EXTERNA Y DE SISTEMAS ---

CREATE TABLE log_validaciones_qr (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    ticket_escaneado VARCHAR(100) NOT NULL,      -- Código leído en la puerta (ej: 'TXN-2051-A')
    fecha_escaneo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resultado_validacion VARCHAR(20) NOT NULL,  -- 'Valida', 'Inválida', 'Ya Usada'
    id_usuario_control INT DEFAULT NULL,         -- Empleado en puerta
    FOREIGN KEY (id_usuario_control) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
);

CREATE TABLE log_actividad_sistema (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    accion_realizada TEXT NOT NULL,              -- Ej: 'Configuración de Precios alterada'
    modulo_afectado VARCHAR(50) NOT NULL,        -- 'USUARIOS', 'CARTELERA', 'TICKETS'
    ip_origen VARCHAR(45) NOT NULL,              -- Dirección IPv4/IPv6 de auditoría
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE SET NULL
);

CREATE TABLE historial_actividad (
    id_actividad INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    tipo_evento VARCHAR(20) NOT NULL,            -- 'RESENA', 'SEGUIDOR', etc.
    id_referencia_usuario INT DEFAULT NULL,
    id_referencia_pelicula INT DEFAULT NULL,
    id_referencia_resena INT DEFAULT NULL,
    texto_breve TEXT DEFAULT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario) ON DELETE CASCADE
);


-- ====================================================================
-- 4. DISPARADORES AUTOMÁTICOS (TRIGGERS DE NEGOCIO)
-- ====================================================================
DELIMITER //

-- Registro automatizado en la bitácora social cuando un usuario publica una reseña
CREATE TRIGGER despues_de_publicar_resena
AFTER INSERT ON resenas
FOR EACH ROW
BEGIN
    INSERT INTO historial_actividad (id_usuario, tipo_evento, id_referencia_pelicula, id_referencia_resena, texto_breve)
    VALUES (NEW.id_usuario, 'RESENA', NEW.id_pelicula, NEW.id_resena, NEW.comentario);
END //

DELIMITER ;


-- ====================================================================
-- 5. INSERCIÓN DE VALORES MAESTROS INICIALES DE CONTROL
-- ====================================================================
-- Cargar el documento maestro por defecto exigido por la tabla de usuarios
INSERT INTO tipos_documento (id_tipo_doc, siglas, descripcion) 
VALUES (1, 'DNI', 'Documento Nacional de Identidad');

-- Cargar los roles mínimos requeridos por tus interfaces del backoffice
INSERT INTO roles (id_role, nombre_rol, descripcion) 
VALUES 
(1, 'ADMINISTRADOR', 'Acceso total al panel administrativo del cine, gestión de salas y permisos'),
(2, 'CLIENTE', 'Acceso exclusivo al aplicativo web B2C, cartelera social y pasarela de compras');

CREATE INDEX idx_interacciones_usuario_favorita 
ON interacciones_peliculas (id_usuario, favorita, fecha_favorito);
CREATE INDEX idx_peliculas_busqueda 
ON peliculas (estado_pelicula, anio_lanzamiento, clasificacion);
CREATE INDEX idx_seguidores_siguiendo 
ON seguidores (id_seguido, id_seguidor);
CREATE INDEX idx_boletas_qr_token 
ON boletas_tickets (codigo_qr_token);
CREATE INDEX idx_transacciones_fecha_estado 
ON transacciones (fecha_transaccion, estado_pago);
CREATE INDEX idx_reembolsos_estado 
ON solicitudes_reembolso (estado_solicitud, fecha_solicitud);
CREATE INDEX idx_funciones_sala_fecha 
ON funciones (id_sala, fecha_hora);
CREATE INDEX idx_asientos_sala_coordenadas 
ON asientos (id_sala, fila, columna);
CREATE INDEX idx_log_sistema_fecha 
ON log_actividad_sistema (fecha_hora, modulo_afectado);
CREATE INDEX idx_historial_actividad_usuario_fecha 
ON historial_actividad (id_usuario, fecha_evento DESC);
CREATE INDEX idx_usuarios_soft_delete ON usuarios(eliminado, id_usuario);
CREATE INDEX idx_peliculas_soft_delete ON peliculas(eliminado, id_pelicula);
-- ====================================================================
-- BLOQUE 1: INSERCIÓN DE SEGURIDAD, CONFIGURACIÓN BASE Y USUARIOS (RBAC)
-- ====================================================================

USE filmate_db;

-- 1.1. ASEGURAR VALORES MAESTROS DE ROLES (Por si acaso)
-- El rol administrador y cliente ya se crean en el script base, pero aseguramos IDs correctos.
INSERT INTO roles (id_role, nombre_rol, descripcion) 
VALUES 
(1, 'ADMINISTRADOR', 'Acceso total al panel administrativo del cine, gestión de salas y permisos')
ON DUPLICATE KEY UPDATE nombre_rol=nombre_rol;

INSERT INTO roles (id_role, nombre_rol, descripcion) 
VALUES 
(2, 'CLIENTE', 'Acceso exclusivo al aplicativo web B2C, cartelera social y pasarela de compras')
ON DUPLICATE KEY UPDATE nombre_rol=nombre_rol;


-- 1.2. INSERCIÓN DE PERMISOS DEL SISTEMA
INSERT INTO permisos (codigo_permiso, descripcion, modulo) VALUES
-- Módulo: Administración y Configuración
('CONFIG_PRECIOS', 'Permite alterar el precio base de las funciones', 'ADMINISTRACIÓN'),
('GESTIONAR_CINES', 'Permite crear, editar o dar de baja cines y salas', 'ADMINISTRACIÓN'),
('GESTIONAR_PELICULAS', 'Permite actualizar el catálogo y sincronizar con TMDb', 'ADMINISTRACIÓN'),
-- Módulo: Ventas y Tickets
('VER_HISTORIAL_TXN', 'Permite visualizar todas las transacciones del sistema', 'VENTAS Y TICKETS'),
('PROCESAR_REEMBOLSOS', 'Permite evaluar y aprobar solicitudes de reembolso', 'VENTAS Y TICKETS'),
('VALIDAR_TICKETS_QR', 'Permite escanear y validar accesos en puerta', 'VENTAS Y TICKETS'),
-- Módulo: Cliente / Operaciones B2C
('COMPRAR_BOLETOS', 'Permite reservar asientos y realizar pagos de funciones', 'OPERACIONES CLIENTE'),
('GESTIONAR_CARRITO', 'Permite interactuar con el carrito de confitería', 'OPERACIONES CLIENTE'),
('PUBLICAR_RESENAS', 'Permite calificar películas y escribir comentarios', 'SOCIAL'),
('SEGUIR_USUARIOS', 'Permite seguir e interactuar con el feed de otros usuarios', 'SOCIAL');


-- 1.3. ASIGNACIÓN DE PERMISOS A ROLES (roles_permisos)
-- Administrador: Recibe absolutamente todos los permisos
INSERT INTO roles_permisos (id_role, id_permiso)
SELECT 1, id_permiso FROM permisos;

-- Cliente: Recibe solo permisos de compra, dulcería y redes sociales
INSERT INTO roles_permisos (id_role, id_permiso)
SELECT 2, id_permiso FROM permisos 
WHERE codigo_permiso IN ('COMPRAR_BOLETOS', 'GESTIONAR_CARRITO', 'PUBLICAR_RESENAS', 'SEGUIR_USUARIOS');


USE filmate_db;

INSERT INTO usuarios (id_usuario, nombre, username, correo, contrasena, id_tipo_doc, numero_documento, telefono, url_perfil, estado_usuario) VALUES
-- --- ADMINISTRADORES (Estilo: Initials basados en su nombre) ---
(1, 'Carlos Mendoza Ruíz', 'carlos_admin', 'carlos.mendoza@filmate.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '47589612', '981234567', 'https://api.dicebear.com/10.x/initials/svg?seed=Carlos+Mendoza', 'ACTIVO'),
(2, 'Ana Sofía Torres', 'ana_admin', 'ana.torres@filmate.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '71452369', '993456781', 'https://api.dicebear.com/10.x/initials/svg?seed=Ana+Sofía+Torres', 'ACTIVO'),
(3, 'Diego Alejandro Ramos', 'diego_admin', 'diego.ramos@filmate.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '40215893', '955123489', 'https://api.dicebear.com/10.x/initials/svg?seed=Diego+Alejandro+Ramos', 'ACTIVO'),

-- --- CLIENTES (Estilo: Bottts de kuki_listo secuenciales del 1 al 10) ---
(4, 'Juan Carlos Palomino', 'juanc_palo', 'juan.palomino@gmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '74859612', '921458763', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_1', 'ACTIVO'),
(5, 'Valeria Belén Espinoza', 'vale_espinoza', 'valeria.es@outlook.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '45123698', '934125789', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_2', 'ACTIVO'),
(6, 'Mateo Sebastián Guerrero', 'mateo_g', 'mguerrero@gmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '70152436', '941258963', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_3', 'ACTIVO'),
(7, 'Camila Fernanda Loli', 'cami_loli', 'camila.loli@hotmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '48965213', '963258147', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_4', 'ACTIVO'),
(8, 'Renzo Gabriel Villanueva', 'renzo_v', 'renzo.villa@gmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '72361458', '974152638', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_5', 'ACTIVO'),
(9, 'María José Barrientos', 'majo_barrientos', 'majo.b@gmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '41526374', '985471236', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_6', 'ACTIVO'),
(10, 'Lucas André Benavides', 'lucas_benavides', 'lucas.bena@outlook.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '75961423', '912347856', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_7', 'ACTIVO'),
(11, 'Andrea Carolina Castro', 'andre_castro', 'andrea.castro@gmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '46321598', '936582147', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_8', 'ACTIVO'),
(12, 'Gonzalo Martín Farfán', 'gonzalo_f', 'gfarfan@gmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '71236985', '998521436', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_9', 'ACTIVO'),
(13, 'Fiorella Beatriz Chávez', 'fio_chavez', 'fiorella.chavez@hotmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 1, '43652198', '954123687', 'https://api.dicebear.com/7.x/bottts/svg?seed=kuki_listo_10', 'ACTIVO');


-- 1.5. ASIGNACIÓN DE ROLES A USUARIOS (usuarios_roles)
INSERT INTO usuarios_roles (id_usuario, id_role) VALUES
-- Admins (IDs 1 al 3 -> Rol 1)
(1, 1),
(2, 1),
(3, 1),
-- Clientes (IDs 4 al 13 -> Rol 2)
(4, 2),
(5, 2),
(6, 2),
(7, 2),
(8, 2),
(9, 2),
(10, 2),
(11, 2),
(12, 2),
(13, 2);
-- ====================================================================
-- BLOQUE 2: INSERCIÓN DE INFRAESTRUCTURA FÍSICA (CINES, SALAS Y ASIENTOS)
-- ====================================================================

USE filmate_db;

-- 2.1. INSERCIÓN DE CINES (4 Sedes con sus URLs de mapas extraídas)
INSERT INTO cines (id_cine, nombre_cine, direccion, horarios_apertura, url_mapa_embebido, estado_cine, observaciones) VALUES
(1, 'Filmate La Molina', 'Av. Javier Prado Este 5400, La Molina', 'Lunes a Domingo: 1:00 PM - 11:00 PM', 'https://www.google.com/maps?q=Av.%20La%20Molina%201300%2C%20La%20Molina&output=embed', 'Activo', 'Sede principal con zona lounge mejorada.'),
(2, 'Filmate Miraflores', 'Av. Alfredo Benavides 430, Miraflores', 'Lunes a Domingo: 1:00 PM - 11:00 PM', 'https://www.google.com/maps?q=Av.%20Larco%201036%2C%20Miraflores&output=embed', 'Activo', 'Ubicación céntrica cerca al Parque Kennedy.'),
(3, 'Filmate San Isidro', 'Av. Camino Real 1251, San Isidro', 'Lunes a Domingo: 1:00 PM - 11:00 PM', 'https://www.google.com/maps?q=Av.%20Conquistadores%20511%2C%20San%20Isidro&output=embed', 'Activo', 'Estacionamiento gratuito por la compra de combos de confitería.'),
(4, 'Filmate Surco', 'Av. Santiago de Surco 3240, Surco', 'Lunes a Domingo: 1:00 PM - 11:00 PM', 'https://www.google.com/maps?q=Av.%20Primavera%202390%2C%20Santiago%20de%20Surco&output=embed', 'Activo', 'Sede con mayor capacidad de salas IMAX.');


-- 2.2. INSERCIÓN DE SALAS (Entre 4 y 6 salas por complejo)
INSERT INTO salas (id_sala, id_cine, nombre_sala, tipo_sala, tipo_formato, capacidad_asientos, estado_sala) VALUES
-- --- Salas para La Molina (Sede 1: 5 salas) ---
(1, 1, 'Sala 1 - Estándar', 'Stand.', '2D', 168, 'Activa'),
(2, 1, 'Sala 2 - 4DX', '4DX', '3D', 168, 'Activa'),
(3, 1, 'Sala 3 - VIP', 'VIP', '2D', 168, 'Activa'),
(4, 1, 'Sala 4 - Estándar', 'Stand.', '3D', 168, 'Activa'),
(5, 1, 'Sala 5 - Estándar', 'Stand.', '2D', 168, 'Activa'),

-- --- Salas para Miraflores (Sede 2: 4 salas) ---
(6, 2, 'Sala 1 - IMAX', 'IMAX', '3D', 168, 'Activa'),
(7, 2, 'Sala 2 - Estándar', 'Stand.', '2D', 168, 'Activa'),
(8, 2, 'Sala 3 - VIP', 'VIP', '2D', 168, 'Activa'),
(9, 2, 'Sala 4 - 4DX', '4DX', '2D', 168, 'Activa'),

-- --- Salas para San Isidro (Sede 3: 4 salas) ---
(10, 3, 'Sala 1 - VIP', 'VIP', '2D', 168, 'Activa'),
(11, 3, 'Sala 2 - Estándar', 'Stand.', '2D', 168, 'Activa'),
(12, 3, 'Sala 3 - Estándar', 'Stand.', '2D', 168, 'Activa'),
(13, 3, 'Sala 4 - Estándar', 'Stand.', '3D', 168, 'Activa'),

-- --- Salas para Surco (Sede 4: 6 salas) ---
(14, 4, 'Sala 1 - IMAX', 'IMAX', '3D', 168, 'Activa'),
(15, 4, 'Sala 2 - 4DX', '4DX', '3D', 168, 'Activa'),
(16, 4, 'Sala 3 - Estándar', 'Stand.', '2D', 168, 'Activa'),
(17, 4, 'Sala 4 - Estándar', 'Stand.', '2D', 168, 'Activa'),
(18, 4, 'Sala 5 - VIP', 'VIP', '2D', 168, 'Activa'),
(19, 4, 'Sala 6 - VIP', 'VIP', '3D', 168, 'Activa');


-- 2.3. GENERACIÓN AUTOMÁTICA DE ASIENTOS (Procedimiento Almacenado Temporal)
DELIMITER //

DROP PROCEDURE IF EXISTS pr_generar_asientos_bloque2 //

CREATE PROCEDURE pr_generar_asientos_bloque2()
BEGIN
    DECLARE v_id_sala INT;
    DECLARE fila_idx INT;
    DECLARE col_idx INT;
    DECLARE v_letra_fila VARCHAR(5);
    
    -- Cursor dinámico que leerá todas las salas registradas arriba
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur_salas CURSOR FOR SELECT id_sala FROM salas;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur_salas;

    read_loop: LOOP
        FETCH cur_salas INTO v_id_sala;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Iterar sobre 12 filas (A=1 hasta L=12)
        SET fila_idx = 1;
        while_filas: WHILE fila_idx <= 12 DO
            
            -- Convertir el índice numérico a letras (A-L)
            SET v_letra_fila = ELT(fila_idx, 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L');
            
            -- Iterar sobre 14 columnas
            SET col_idx = 1;
            while_columnas: WHILE col_idx <= 14 DO
                
                -- Insertar la butaca física (Todas 'Regular' por defecto, Estado 'Activo')
                INSERT INTO asientos (id_sala, fila, columna, tipo_asiento, estado_asiento)
                VALUES (v_id_sala, v_letra_fila, col_idx, 'Regular', 'Activo');
                
                SET col_idx = col_idx + 1;
            END WHILE while_columnas;
            
            SET fila_idx = fila_idx + 1;
        END WHILE while_filas;

    END LOOP read_loop;

    CLOSE cur_salas;
END //

DELIMITER ;

-- Ejecutar el generador para poblar la tabla `asientos` (Poblará dinámicamente las 19 salas)
CALL pr_generar_asientos_bloque2();

-- Limpieza: Eliminar el procedimiento para no dejar rastro en el esquema
DROP PROCEDURE IF EXISTS pr_generar_asientos_bloque2;
-- ====================================================================
-- BLOQUE 3: CATÁLOGO DE PELÍCULAS (GÉNEROS Y PELÍCULAS DESDE TMDb)
-- ====================================================================

USE filmate_db;

-- Inserción de Géneros Oficiales TMDb
INSERT INTO generos (id_genero, nombre_genero) VALUES (28, 'Acción') ON DUPLICATE KEY UPDATE nombre_genero='Acción';
INSERT INTO generos (id_genero, nombre_genero) VALUES (12, 'Aventura') ON DUPLICATE KEY UPDATE nombre_genero='Aventura';
INSERT INTO generos (id_genero, nombre_genero) VALUES (16, 'Animación') ON DUPLICATE KEY UPDATE nombre_genero='Animación';
INSERT INTO generos (id_genero, nombre_genero) VALUES (35, 'Comedia') ON DUPLICATE KEY UPDATE nombre_genero='Comedia';
INSERT INTO generos (id_genero, nombre_genero) VALUES (80, 'Crimen') ON DUPLICATE KEY UPDATE nombre_genero='Crimen';
INSERT INTO generos (id_genero, nombre_genero) VALUES (99, 'Documental') ON DUPLICATE KEY UPDATE nombre_genero='Documental';
INSERT INTO generos (id_genero, nombre_genero) VALUES (18, 'Drama') ON DUPLICATE KEY UPDATE nombre_genero='Drama';
INSERT INTO generos (id_genero, nombre_genero) VALUES (10751, 'Familia') ON DUPLICATE KEY UPDATE nombre_genero='Familia';
INSERT INTO generos (id_genero, nombre_genero) VALUES (14, 'Fantasía') ON DUPLICATE KEY UPDATE nombre_genero='Fantasía';
INSERT INTO generos (id_genero, nombre_genero) VALUES (36, 'Historia') ON DUPLICATE KEY UPDATE nombre_genero='Historia';
INSERT INTO generos (id_genero, nombre_genero) VALUES (27, 'Terror') ON DUPLICATE KEY UPDATE nombre_genero='Terror';
INSERT INTO generos (id_genero, nombre_genero) VALUES (10402, 'Música') ON DUPLICATE KEY UPDATE nombre_genero='Música';
INSERT INTO generos (id_genero, nombre_genero) VALUES (9648, 'Misterio') ON DUPLICATE KEY UPDATE nombre_genero='Misterio';
INSERT INTO generos (id_genero, nombre_genero) VALUES (10749, 'Romance') ON DUPLICATE KEY UPDATE nombre_genero='Romance';
INSERT INTO generos (id_genero, nombre_genero) VALUES (878, 'Ciencia ficción') ON DUPLICATE KEY UPDATE nombre_genero='Ciencia ficción';
INSERT INTO generos (id_genero, nombre_genero) VALUES (10770, 'Película de TV') ON DUPLICATE KEY UPDATE nombre_genero='Película de TV';
INSERT INTO generos (id_genero, nombre_genero) VALUES (53, 'Suspense') ON DUPLICATE KEY UPDATE nombre_genero='Suspense';
INSERT INTO generos (id_genero, nombre_genero) VALUES (10752, 'Bélica') ON DUPLICATE KEY UPDATE nombre_genero='Bélica';
INSERT INTO generos (id_genero, nombre_genero) VALUES (37, 'Western') ON DUPLICATE KEY UPDATE nombre_genero='Western';

-- Película: Amos del Universo
 INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (1, 'Amos del Universo', 2026, 141, '+14', 'EN CARTELERA', 'https://image.tmdb.org/t/p/w500/hNLKuennkGtlWvqU6Ko4Z6X8JHg.jpg', 'https://image.tmdb.org/t/p/original/eQySd26OW7UmCuaeBOL7qy6foMn.jpg', 'https://www.youtube.com/embed/K2p_Xz8i2Uo?autoplay=1', 'En las regiones más lejanas del espacio, el reino de Eternia está amenazado por el villano Skeletor y sus traviesos ejércitos de oscuridad. Para salvar el reino de su padre y proteger las vidas de sus seres queridos, el joven príncipe Adam tiene que recuperar una espada mítica y convertirse en el legendario guerrero conocido como "He-Man".', 'Nicholas Galitzine, Jared Leto, Camila Mendes, Idris Elba, Alison Brie', 'Travis Knight');
 -- Géneros de: Amos del Universo
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (1, 28);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (1, 14);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (1, 878);

-- Película: Paucartambo
INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (2, 'Paucartambo', 2024, 71, 'APT', 'EN CARTELERA', 'https://image.tmdb.org/t/p/w500/cCgDW9L09y7Z9A0pyMaxGWglZPq.jpg', 'https://image.tmdb.org/t/p/original/nXsZSDDMuAIwzYc0yTRaD9xE4sw.jpg', 'https://www.youtube.com/embed/was0bnFEKyI?autoplay=1', '“Paucartambo” es un documental observacional desarrollado en la Fiesta de la Virgen del Carmen de Paucartambo, a través de un bailarin Maqta y la comparsa Qollas, se retratan intensos encuentros que reflejan la profundidad entre la cosmovisión andina y el sincretismo peruano.', 'Fabricio Quillahuaman, Augusto Casafranca', 'William Bustos');
-- Géneros de: Paucartambo
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (2, 99);

-- Película: Scary Movie Terrorificamente Incorrecta
 INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (3, 'Scary Movie Terrorificamente Incorrecta', 2026, 96, '+18', 'EN CARTELERA', 'https://image.tmdb.org/t/p/w500/vUPE82BWRZwq6M5Xc9UNuf8AffK.jpg', 'https://image.tmdb.org/t/p/original/lj6AaDqDUbzm2XJltFNHeAm2uXN.jpg', 'https://www.youtube.com/embed/HMTKiPCKgpw?si=nnqX86lvlfv_fV6Z', 'Veintiséis años después de conseguir escapar de un asesino enmascarado sospechosamente familiar, el Core Four están de vuelta en el punto de mira del asesino y ninguna película de terror está a salvo.', 'Marlon Wayans, Shawn Wayans, Anna Faris, Regina Hall, Damon Wayans Jr.', 'Michael Tiddes');
 -- Géneros de: Scary Movie Terrorificamente Incorrecta
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (3, 35);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (3, 27);

-- Película: Amando a Amanda
INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (4, 'Amando a Amanda', 2026, 90, '+14', 'ACTIVO', 'https://image.tmdb.org/t/p/w500/ik3lBmw2s8ZazGdHBMaqGDdAaLe.jpg', 'default_banner.png', 'https://www.youtube.com/embed/6FC47ORT0PU?si=WGwFonOWo_iufJz2', 'Fernando está convencido de una cosa: Amanda es el amor de su vida. Lo supo cuando eran niños, lo confirmó al casarse con ella y lo sigue creyendo incluso después de separarse. Amanda es brillante, talentosa y absolutamente impredecible; vive entre impulsos, risas, excesos y una intensidad que vuelve cualquier situation… inolvidable.', 'Gianella Neyra, Giovanni Ciccia, Rodrigo Sánchez-Patiño, Nacho Di Marco, Fiorella Diaz', 'Ani Alva Helfer');
-- Géneros de: Amando a Amanda
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (4, 35);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (4, 10749);

-- Película: Backrooms
INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (5, 'Backrooms', 2026, 110, '+14', 'ACTIVO', 'https://image.tmdb.org/t/p/w500/mIeeEL8WnkmLbNjFIs7uo55VF9Q.jpg', 'default_banner.png', 'https://www.youtube.com/embed/j6xBUJSm_S8?si=3vFf0osNzsQ-g2d5', 'Basado en el fenómeno viral de internet. Un grupo de jóvenes termina atrapado por error en un laberinto interminable de oficinas vacías con paredes amarillas, luces fluorescentes parpadeantes y una presencia siniestra de la que no hay salida.', 'Bradley Gareth, Kane Parsons', 'Kane Parsons');
-- Géneros de: Backrooms
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (5, 27);

-- Película: The Mandalorian and Grogu
INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (6, 'The Mandalorian and Grogu', 2026, 133, 'APT', 'ACTIVO', 'https://image.tmdb.org/t/p/w500/sWitU9IjgFwf6y1OrI0zUaL3GNa.jpg', 'https://image.tmdb.org/t/p/original/6zg7A9ICOthNR2TSXlT51KvXrsA.jpg', 'https://www.youtube.com/embed/bDmr-8CaeBg?autoplay=1', 'Continuación de la serie "The Mandalorian" en forma de película. El Imperio ha caído y los señores de la guerra imperiales siguen dispersos por toda la galaxia. Mientras la incipiente Nueva República trabaja para proteger todo por lo que luchó la Rebelión, ha reclutado la ayuda del legendario cazarrecompensas mandaloriano Din Djarin y su joven aprendiz Grogu.', 'Pedro Pascal, Jeremy Allen White, Sigourney Weaver, Brendan Wayne, Lateef Crowder', 'Jon Favreau');
-- Géneros de: The Mandalorian and Grogu
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (6, 28);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (6, 12);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (6, 878);

-- Película: Obsesion
INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (7, 'Obsesion', 2026, 108, '+14', 'ACTIVO', 'https://image.tmdb.org/t/p/w500/ohi9xvbBUymM4SuIOSlt1xbLRQQ.jpg', 'https://image.tmdb.org/t/p/original/rZfmzpixLKLR3Hg2u0WgC7XLFl8.jpg', 'https://www.youtube.com/embed/5MBu6Xhuj38?autoplay=1', 'El anhelo romántico desesperado de un chico por su amor platónico de toda la vida desencadena un siniestro hechizo: Niki se vuelve irracionalmente obsesiva hasta convertirse en la sombra de Bear. Una fantasía aparentemente inofensiva que se convertirá en una perturbadora pesadilla.', 'Michael Johnston, Inde Navarrette, Cooper Tomlinson, Megan Lawless, Andy Richter', 'Curry Barker');
-- Géneros de: Obsesion
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (7, 27);

-- Película: Las Ovejas Detectives
INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (8, 'Las Ovejas Detectives', 2026, 110, 'APT', 'ACTIVO', 'https://image.tmdb.org/t/p/w500/kMJ4h39xe1fEzbLSt5FJCtEqb2H.jpg', 'https://image.tmdb.org/t/p/original/t6O6XWelu27BD0OmIDCCufZZT6d.jpg', 'https://www.youtube.com/embed/826SRt1CFbg?autoplay=1', 'Cada noche, un pastor lee en voz alta un asesinato misterioso, fingiendo que sus ovejas pueden entenderlo. Cuando lo encuentran muerto, las ovejas se dan cuenta enseguida de que ha sido un asesinato y creen saber cómo resolverlo.', 'Hugh Jackman, Julia Louis-Dreyfus, Emma Thompson, Nicholas Braun, Nicholas Galitzine', 'Kyle Balda');
-- Géneros de: Las Ovejas Detectives
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (8, 35);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (8, 10751);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (8, 9648);

-- Película: El diablo viste a la Moda 2
INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (9, 'El diablo viste a la Moda 2', 2006, 120, '+14', 'ACTIVO', 'https://image.tmdb.org/t/p/w500/rdvPsRItlhErfKF8Y0f0wjnxUzz.jpg', 'https://image.tmdb.org/t/p/original/gkh6Nt8DtY1XT4gQsyFq9XAVJlJ.jpg', 'https://www.youtube.com/embed/aXdjJbVrJeg?si=DutLH3MEc4qsqxkh', 'Sigue la lucha de Miranda Priestly contra Emily Charlton, su ex asistente convertida en ejecutiva rival, mientras compiten por los ingresos por publicidad en medio de la decadencia de los medios impresos y Miranda se acerca a la jubilación.', 'Meryl Streep, Anne Hathaway, Emily Blunt, Stanley Tucci, Simon Baker', 'David Frankel');
-- Géneros de: El diablo viste a la Moda 2
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (9, 18);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (9, 35);

-- Película: Michael
INSERT INTO peliculas (id_pelicula, titulo, anio_lanzamiento, duracion_minutos, clasificacion, estado_pelicula, url_poster, url_banner, url_trailer, sinopsis, elenco, director) VALUES (10, 'Michael', 2026, 127, '+14', 'ACTIVO', 'https://image.tmdb.org/t/p/w500/2uK36ujoDXOfNiJ5Yp3raVprB51.jpg', 'https://image.tmdb.org/t/p/original/xBT0oNq6rsTFv4SxG5uGRIEOrq6.jpg', 'https://www.youtube.com/embed/o1HQSh6zZ8s?autoplay=1', 'El viaje de Michael Jackson más allá de la música, desde el descubrimiento de su extraordinario talento como líder de los Jackson Five hasta convertirse en una visionaria estrella cuya ambición creativa despertó un incansable afán por consagrarse como el mayor icono de la industria del entretenimiento.', 'Jaafar Jackson, Colman Domingo, Nia Long, Juliano Krue Valdi, Miles Teller', 'Antoine Fuqua');
-- Géneros de: Michael
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (10, 10402);
INSERT INTO peliculas_generos (id_pelicula, id_genero) VALUES (10, 18);

-- ====================================================================
-- BLOQUE 4: OPERACIONES, DULCERÍA Y SIMULACIÓN SOCIAL MASIVA (MÓDULO FINAL)
-- ====================================================================

USE filmate_db;

-- 4.1. MÓDULO CONFITERÍA: CATEGORÍAS Y CATÁLOGO AMPLIADO
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE carrito_confiteria;
TRUNCATE TABLE detalle_boleta_confiteria;
TRUNCATE TABLE productos_confiteria;
TRUNCATE TABLE categorias_confiteria;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO categorias_confiteria (id_categoria_confi, nombre_categoria) VALUES
(1, 'Combos'), (2, 'Canchita'), (3, 'Bebidas'), (4, 'Dulces');

INSERT INTO productos_confiteria (id_producto, id_categoria_confi, nombre_producto, descripcion, precio, url_imagen, stock) VALUES
-- --- CATEGORÍA 1: COMBOS ---
(1, 1, 'Combo Personal Filmate', '1 Canchita Grande Salada + 1 Gaseosa Mediana 32oz', 26.00, 'https://i.ibb.co/Hfn0Kx0Z/Chat-GPT-Image-16-jun-2026-01-04-11.png', 5000),
(2, 1, 'Combo Pareja de Estreno', '1 Canchita Gigante + 2 Gaseosas Medianas + 1 Chocolate M&M', 45.00, 'https://i.ibb.co/gLbZpKTF/2d7e2465-9ba4-469f-ab03-f4fb06469af9.png', 3500),
(3, 1, 'Combo Familiar Filmate', '2 Canchitas Medianas + 4 Gaseosas Medianas + 1 Hot Dog Gigante', 75.00, 'https://i.ibb.co/2YPvHkTG/Chat-GPT-Image-16-jun-2026-01-08-27.png', 2000),
(4, 1, 'Combo Hot Dog Simple', '1 Hot Dog Clásico + 1 Gaseosa Mediana 32oz', 22.00, 'https://i.ibb.co/N2JmkqHX/7ba649df-a8ff-4323-8ed2-c6bcc6c14600.png', 1500),
(5, 1, 'Combo Kids Animación', '1 Canchita Chica Dulce + 1 Frugos en caja + 1 Juguete de colección', 28.00, 'https://i.ibb.co/hxwgW1Pc/cf26e7fd-cdc3-40c3-b2c2-b4fc0277e13e.png', 1800),

-- --- CATEGORÍA 2: CANCHITA (POPCORN) ---
(6, 2, 'Canchita Popcorn Familiar Salada', 'Balde gigante de canchita salada clásica', 18.00, 'https://i.ibb.co/wxCp3K3/6fc5808c-8906-4534-ad53-13cd3879cee5.png', 9000),
(7, 2, 'Canchita Popcorn Familiar Dulce', 'Balde gigante de canchita acaramelada crujiente', 20.00, 'https://i.ibb.co/wxCp3K3/6fc5808c-8906-4534-ad53-13cd3879cee5.png', 8500),
(8, 2, 'Canchita Popcorn Mediana Mix', 'Bolsa mediana mitad dulce y mitad salada', 15.00, 'https://i.ibb.co/wxCp3K3/6fc5808c-8906-4534-ad53-13cd3879cee5.png', 6000),
(9, 2, 'Canchita Popcorn Porción Chica', 'Bolsa personal de canchita salada', 10.00, 'https://i.ibb.co/wxCp3K3/6fc5808c-8906-4534-ad53-13cd3879cee5.png', 4000),

-- --- CATEGORÍA 3: BEBIDAS ---
(10, 3, 'Gaseosa Gigante XL', 'Vaso de 32oz (Coca-Cola, Inka Cola, Sprite)', 11.00, 'https://i.ibb.co/DP9Scvj9/Chat-GPT-Image-16-jun-2026-01-16-24.png', 8000),
(11, 3, 'Gaseosa Mediana', 'Vaso de 22oz (Coca-Cola, Inka Cola, Fanta)', 9.00, 'https://i.ibb.co/DP9Scvj9/Chat-GPT-Image-16-jun-2026-01-16-24.png', 7500),
(12, 3, 'Agua San Luis Sin Gas', 'Botella personal de 500ml', 6.00, 'https://i.ibb.co/DP9Scvj9/Chat-GPT-Image-16-jun-2026-01-16-24.png', 3000),
(13, 3, 'Chicha Morada Natural', 'Vaso mediano de chicha morada de la casa', 8.50, 'https://i.ibb.co/DP9Scvj9/Chat-GPT-Image-16-jun-2026-01-16-24.png', 2500),

-- --- CATEGORÍA 4: DULCES Y SNACKS ---
(14, 4, 'Chocolates Sublime Pack', 'Paquete de 3 unidades ideales para compartir', 8.50, 'https://i.ibb.co/whRDDpRM/Chat-GPT-Image-16-jun-2026-01-17-44.png', 4000),
(15, 4, 'M&M Compartir', 'Bolsa grande de chocolates con maní', 12.00, 'https://i.ibb.co/whRDDpRM/Chat-GPT-Image-16-jun-2026-01-17-44.png', 3000),
(16, 4, 'Papas Lay Clásicas', 'Bolsa familiar de papas fritas saladas', 7.50, 'https://i.ibb.co/whRDDpRM/Chat-GPT-Image-16-jun-2026-01-17-44.png', 3500),
(17, 4, 'Gomitas Ambrosoli Ácidas', 'Paquete familiar de gomitas de ositos frutales', 6.50, 'https://i.ibb.co/whRDDpRM/Chat-GPT-Image-16-jun-2026-01-17-44.png', 2000);


-- 4.2. PROGRAMACIÓN AUTOMÁTICA DE CARTELERA DIARIA (06 al 16 de Junio, 2026)
DELIMITER //

DROP PROCEDURE IF EXISTS pr_generar_cartelera_masiva //

CREATE PROCEDURE pr_generar_cartelera_masiva()
BEGIN
    DECLARE v_fecha_inicio DATE DEFAULT '2026-06-06';
    DECLARE v_fecha_fin DATE DEFAULT '2026-06-16';
    DECLARE v_fecha_actual DATE;
    DECLARE v_id_sala INT;
    DECLARE v_tipo_sala VARCHAR(20);
    DECLARE v_precio DECIMAL(10,2);
    DECLARE v_pelicula_idx INT DEFAULT 1;
    
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur_salas CURSOR FOR SELECT id_sala, tipo_sala FROM salas;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SET v_fecha_actual = v_fecha_inicio;

    while_fechas: WHILE v_fecha_actual <= v_fecha_fin DO
        OPEN cur_salas;
        SET done = FALSE;
        
        read_loop: LOOP
            FETCH cur_salas INTO v_id_sala, v_tipo_sala;
            IF done THEN
                LEAVE read_loop;
            END IF;
            
            IF v_tipo_sala = 'IMAX' THEN SET v_precio = 35.00;
            ELSEIF v_tipo_sala = 'VIP' THEN SET v_precio = 35.00;
            ELSEIF v_tipo_sala = '4DX' THEN SET v_precio = 25.00;
            ELSE SET v_precio = 15.00;
            END IF;

            -- Función 1: Tarde (4:00 PM)
            INSERT INTO funciones (id_pelicula, id_sala, fecha_hora, precio_base)
            VALUES (((v_pelicula_idx) % 10) + 1, v_id_sala, CONCAT(v_fecha_actual, ' 16:00:00'), v_precio);
            
            -- Función 2: Noche (8:30 PM)
            INSERT INTO funciones (id_pelicula, id_sala, fecha_hora, precio_base)
            VALUES (((v_pelicula_idx + 3) % 10) + 1, v_id_sala, CONCAT(v_fecha_actual, ' 20:30:00'), v_precio);

            SET v_pelicula_idx = v_pelicula_idx + 1;
        END LOOP read_loop;
        
        CLOSE cur_salas;
        SET v_fecha_actual = DATE_ADD(v_fecha_actual, INTERVAL 1 DAY);
    END WHILE while_fechas;
END //

DELIMITER ;

CALL pr_generar_cartelera_masiva();
DROP PROCEDURE IF EXISTS pr_generar_cartelera_masiva;


-- 4.3. INSTANCIACIÓN DE INVENTARIO DE BUTACAS POR FUNCIÓN ('Disponible')
DELIMITER //

DROP PROCEDURE IF EXISTS pr_mapear_asientos_funciones //

CREATE PROCEDURE pr_mapear_asientos_funciones()
BEGIN
    DECLARE v_id_funcion INT;
    DECLARE v_id_sala INT;
    DECLARE done INT DEFAULT FALSE;
    
    DECLARE cur_funciones CURSOR FOR SELECT id_funcion, id_sala FROM funciones;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur_funciones;

    read_loop: LOOP
        FETCH cur_funciones INTO v_id_funcion, v_id_sala;
        IF done THEN
            LEAVE read_loop;
        END IF;

        INSERT INTO asientos_funciones (id_funcion, id_asiento, estado)
        SELECT v_id_funcion, id_asiento, 'Disponible'
        FROM asientos
        WHERE id_sala = v_id_sala;

    END LOOP read_loop;

    CLOSE cur_funciones;
END //

DELIMITER ;

CALL pr_mapear_asientos_funciones();
DROP PROCEDURE IF EXISTS pr_mapear_asientos_funciones;


-- 4.4. RED SOCIAL: RELACIONES DE SEGUIDORES Y 50 RESEÑAS DE LA COMUNIDAD
INSERT INTO seguidores (id_seguidor, id_seguido) VALUES
(4, 5), (4, 6), (4, 7), (5, 4), (5, 6), (5, 8), (6, 4), (6, 5), (6, 9), (7, 4), (7, 8), (7, 10),
(8, 5), (8, 7), (8, 11), (9, 6), (9, 10), (9, 12), (10, 7), (10, 9), (10, 13), (11, 8), (11, 12),
(12, 9), (12, 11), (13, 10), (13, 4);

TRUNCATE TABLE resenas;

INSERT INTO resenas (id_usuario, id_pelicula, puntuacion_estrellas, comentario) VALUES
-- Película 1: Amos del Universo
(4, 1, 4, 'Excelente despliegue de Eternia, superó mis expectativas nostálgicas.'),
(5, 1, 5, 'Visualmente es una obra maestra de la ciencia ficción moderna. Los efectos son brutales.'),
(6, 1, 3, 'Está buena, pero el ritmo decae un poco a la mitad de la película.'),
(7, 1, 4, 'La actuación de Skeletor es magnífica, se roba cada escena en la que aparece.'),
(8, 1, 2, 'Mucho efecto especial pero la historia se siente algo vacía para mi gusto.'),
-- Película 2: Paucartambo
(9, 2, 4, 'Un documental hermoso que plasma el misticismo andino de Paucartambo de forma muy respetuosa.'),
(10, 2, 5, 'La fotografía y el sonido de las danzas folclóricas te transportan por completo a la festividad.'),
(11, 2, 4, 'Espectacular retrato de la cosmovisión peruana y el sincretismo cultural.'),
(12, 2, 3, 'Interesante a nivel cultural, aunque el formato observacional se me hizo un poco lento.'),
(13, 2, 5, 'Una joya del cine documental peruano. Totalmente recomendada para ver en pantalla grande.'),
-- Película 3: Scary Movie Terrorificamente Incorrecta
(4, 3, 3, 'Chistes muy buenos y subidos de tono, aunque abusa de los clichés por momentos.'),
(5, 3, 4, 'Hacía años que no me reía tanto en el cine, se burla de todas las películas modernas de terror.'),
(6, 3, 2, 'Un humor demasiado absurdo e incorrecto, no es para todo tipo de público.'),
(7, 3, 4, 'Cumple con creces lo que promete: risas irreverentes y parodias brutales.'),
(8, 3, 3, 'Tiene momentos muy divertidos, pero algunas bromas se sienten un poco desfasadas.'),
-- Película 4: Amando a Amanda
(9, 4, 5, 'Me reí demasiado. Gianella Neyra y Giovanni Ciccia tienen una química brillante en pantalla.'),
(10, 4, 4, 'Una comedia romántica peruana muy bien lograda y con un ritmo excelente.'),
(11, 4, 4, 'Los diálogos se sienten naturales y las situaciones absurdas están muy bien manejadas.'),
(12, 4, 3, 'Es entretenida para pasar el rato, pero el guion no propone nada nuevo en el género.'),
(13, 4, 5, 'La mejor comedia de la temporada. Los giros de la trama te mantienen enganchado.'),
-- Película 5: Backrooms
(4, 5, 5, 'Backrooms (2026) mantiene una atmósfera opresiva espectacular. Kane Parsons es un genio.'),
(5, 5, 4, 'El diseño de producción y el sonido te envuelven en una tensión constante de la que no sales.'),
(6, 5, 5, 'Una genialidad de terror psicológico que redefine el fenómeno de los creepypastas de internet.'),
(7, 5, 3, 'Da mucho miedo y la ambientación es impecable, pero el final me dejó con dudas.'),
(8, 5, 4, 'Hacía tiempo que una película no me generaba tanta ansiedad en el cine. Excelente.'),
-- Película 6: The Mandalorian and Grogu
(9, 6, 5, 'Ver a Grogu en formato IMAX es lo mejor que me pasó en el año. Maravilla cinematográfica.'),
(10, 6, 5, 'Mantiene la esencia pura de la trilogía original de Star Wars con acción moderna increíble.'),
(11, 6, 4, 'Un viaje galáctico fantástico de principio a fin, ideal para los fanáticos de la serie.'),
(12, 6, 4, 'Los efectos prácticos y las batallas espaciales se ven de nivel absoluto en el cine.'),
(13, 6, 3, 'Muy entretenida y épica, aunque se apoya demasiado en el fan service para avanzar.'),
-- Película 7: Obsesion
(4, 7, 2, 'Obsesion se vuelve muy predecible a mitad de camino, aunque tiene un par de buenos sustos.'),
(5, 7, 3, 'Comienza muy bien con el misterio del hechizo, pero el desenlace se siente apresurado.'),
(6, 7, 4, 'Una atmósfera perturbadora excelente que muta en una pesadilla claustrofóbica genial.'),
(7, 7, 3, 'Cumple para los amantes del terror psicológico pero no aporta nada revolucionario.'),
(8, 7, 1, 'Lamentable guion y actuaciones planas. Me aburrí bastante.'),
-- Película 8: Las Ovejas Detectives
(9, 8, 4, 'Las Ovejas Detectives es ingeniosa y divertida para disfrutar el fin de semana con amigos.'),
(10, 8, 4, 'Un concepto sumamente original que combina la comedia británica con el misterio clásico de Agatha Christie.'),
(11, 8, 5, 'Hugh Jackman y Emma Thompson están increíbles dándoles vida a estos personajes.'),
(12, 8, 3, 'Es simpática y tiene un humor familiar bastante decente, ideal para pasar la tarde.'),
(13, 8, 4, 'Me sorprendió gratamente la resolución del misterio criminal. Muy divertida.'),
-- Película 9: El diablo viste a la Moda 2
(4, 9, 1, 'En el vertiginoso mundo de la moda en Nueva York... Destrozaron la original, es una película terrible de verdad.'),
(5, 9, 2, 'Meryl Streep brilla como siempre, pero el guion fuerza demasiado las situaciones de esta secuela.'),
(6, 9, 1, 'Innecesaria por donde se le mire. No se acerca en lo absoluto al impacto de la primera entrega.'),
(7, 9, 3, 'Tiene vestuarios increíbles y buena música, pero la trama se siente repetitiva y floja.'),
(8, 9, 2, 'Una decepción comercial que solo busca lucrar con la nostalgia de un clásico moderno.'),
-- Película 10: Michael
(9, 10, 5, 'Jaafar Jackson captura la esencia de Michael de forma impactante. Las recreaciones de conciertos son una locura.'),
(10, 10, 5, 'Una biografía cinematográfica monumental y respetuosa con el legado musical del Rey del Pop.'),
(11, 10, 5, 'La dirección de Antoine Fuqua es perfecta para retratar la magnitud creativa de este ícono.'),
(12, 10, 4, 'Impresionante despliegue coreográfico y técnico. Te mantiene pegado al asiento las dos horas.'),
(13, 10, 4, 'Una montaña rusa de emociones que rinde tributo a su genialidad musical de forma espectacular.');


-- 4.5. PROCESAMIENTO TRANSACCIONAL MASIVO (Simulación de Compras)
DELIMITER //

DROP PROCEDURE IF EXISTS pr_simular_compras_masivas //

CREATE PROCEDURE pr_simular_compras_masivas()
BEGIN
    DECLARE v_id_txn INT DEFAULT 1;
    DECLARE v_id_user INT;
    DECLARE v_id_func INT;
    DECLARE v_precio_base DECIMAL(10,2);
    DECLARE v_id_asiento INT;
    DECLARE v_monto_tkts DECIMAL(10,2);
    DECLARE v_monto_confi DECIMAL(10,2);
    DECLARE v_monto_total DECIMAL(10,2);
    DECLARE done INT DEFAULT FALSE;
    
    DECLARE cur_ventas CURSOR FOR SELECT id_funcion, precio_base FROM funciones LIMIT 45;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur_ventas;

    read_loop: LOOP
        FETCH cur_ventas INTO v_id_func, v_precio_base;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET v_id_user = 4 + (v_id_txn % 10);
        SET v_monto_tkts = v_precio_base * 2;
        
        IF (v_id_txn % 2 = 0) THEN SET v_monto_confi = 45.00;
        ELSE SET v_monto_confi = 26.00;
        END IF;
        
        SET v_monto_total = v_monto_tkts + v_monto_confi;

        INSERT INTO transacciones (id_transaccion, id_usuario, id_funcion, monto_boletos, monto_confiteria, monto_total, estado_pago, metodo_pago)
        VALUES (v_id_txn, v_id_user, v_id_func, v_monto_tkts, v_monto_confi, v_monto_total, 'Aprobado', CONCAT('Visa **** ', 3000 + v_id_txn));

        SELECT id_asiento INTO v_id_asiento 
        FROM asientos_funciones 
        WHERE id_funcion = v_id_func AND estado = 'Disponible' 
        LIMIT 1;

        UPDATE asientos_funciones SET estado = 'Ocupado' WHERE id_funcion = v_id_func AND id_asiento = v_id_asiento;
        
        INSERT INTO detalle_boleta_asientos (id_transaccion, id_asiento, ingresado) VALUES (v_id_txn, v_id_asiento, FALSE);
        
        INSERT INTO detalle_boleta_confiteria (id_transaccion, id_producto, cantidad, precio_unitario) 
        VALUES (v_id_txn, IF(v_id_txn % 2 = 0, 2, 1), 1, v_monto_confi);

        INSERT INTO boletas_tickets (id_transaccion, codigo_qr_token, estado_ticket)
        VALUES (v_id_txn, CONCAT('QR-FILMATE-TXN', v_id_txn, '-X92'), 'Valido');

        SET v_id_txn = v_id_txn + 1;
    END LOOP read_loop;

    CLOSE cur_ventas;
END //

DELIMITER ;

CALL pr_simular_compras_masivas();
DROP PROCEDURE IF EXISTS pr_simular_compras_masivas;


-- ====================================================================
-- 4.6. SIMULACIÓN MASIVA DE TRANSACCIONES DISTRIBUIDAS POR DÍA
--      Genera N transacciones diarias con fecha, hora, usuario, función,
--      montos y confitería variados, en el rango [p_fecha_inicio, p_fecha_fin].
--      Inserta cabecera + detalle de asientos + detalle de confitería + ticket.
-- ====================================================================
USE filmate_db;

DELIMITER //

DROP PROCEDURE IF EXISTS pr_simular_compras_por_dia //

CREATE PROCEDURE pr_simular_compras_por_dia(
    IN p_fecha_inicio DATE,
    IN p_fecha_fin   DATE,
    IN p_txn_por_dia INT
)
BEGIN
    DECLARE v_id_txn INT;
    DECLARE v_id_user INT;
    DECLARE v_id_func INT;
    DECLARE v_precio_base DECIMAL(10,2);
    DECLARE v_id_asiento INT;
    DECLARE v_id_producto INT;
    DECLARE v_monto_tkts DECIMAL(10,2);
    DECLARE v_monto_confi DECIMAL(10,2);
    DECLARE v_monto_total DECIMAL(10,2);
    DECLARE v_hora INT;
    DECLARE v_minuto INT;
    DECLARE v_segundo INT;
    DECLARE v_fecha_txn DATETIME;
    DECLARE v_idx_dia INT;
    DECLARE v_idx_txn INT;
    DECLARE v_idx_iter INT DEFAULT 0;
    DECLARE v_total_dias INT;
    DECLARE v_total_iter INT;
    DECLARE v_total_funciones INT;
    DECLARE done INT DEFAULT FALSE;

    DECLARE cur_funciones CURSOR FOR SELECT id_funcion, precio_base FROM funciones ORDER BY id_funcion;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SELECT COUNT(*) INTO v_total_funciones FROM funciones;

    IF v_total_funciones = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay funciones registradas en el sistema.';
    END IF;

    IF p_fecha_fin < p_fecha_inicio THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha fin no puede ser menor a la fecha inicio.';
    END IF;

    SET v_total_dias = DATEDIFF(p_fecha_fin, p_fecha_inicio) + 1;
    SET v_total_iter = v_total_dias * p_txn_por_dia;
    SELECT IFNULL(MAX(id_transaccion), 0) + 1 INTO v_id_txn FROM transacciones;

    OPEN cur_funciones;

    read_loop: LOOP
        IF v_idx_iter >= v_total_iter THEN
            LEAVE read_loop;
        END IF;

        FETCH cur_funciones INTO v_id_func, v_precio_base;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET v_idx_dia = v_idx_iter DIV p_txn_por_dia;
        SET v_idx_txn = v_idx_iter MOD p_txn_por_dia;

        SET v_id_user     = 4 + ((v_id_txn + v_idx_iter) MOD 10);
        SET v_id_producto = 1 + ((v_id_txn + v_idx_iter) MOD 17);
        SET v_monto_tkts  = v_precio_base * (1 + ((v_id_txn + v_idx_iter) MOD 3));
        SET v_monto_confi = IF((v_id_txn + v_idx_iter) MOD 2 = 0, 45.00, 26.00);
        SET v_monto_total = v_monto_tkts + v_monto_confi;

        SET v_hora    = 9  + ((v_id_txn * 3  + v_idx_txn * 5 ) MOD 14);
        SET v_minuto  =      ((v_id_txn * 7  + v_idx_txn * 11) MOD 60);
        SET v_segundo =      ((v_id_txn * 13 + v_idx_txn * 17) MOD 60);

        SET v_fecha_txn = CONCAT(
            DATE_FORMAT(DATE_ADD(p_fecha_inicio, INTERVAL v_idx_dia DAY), '%Y-%m-%d'),
            ' ', LPAD(v_hora, 2, '0'), ':', LPAD(v_minuto, 2, '0'), ':', LPAD(v_segundo, 2, '0')
        );

        INSERT INTO transacciones (id_usuario, id_funcion, monto_boletos, monto_confiteria, monto_total, estado_pago, metodo_pago, fecha_transaccion)
        VALUES (v_id_user, v_id_func, v_monto_tkts, v_monto_confi, v_monto_total, 'Aprobado',
                CONCAT('Visa **** ', LPAD(3000 + ((v_id_txn * 11) MOD 9999), 4, '0')), v_fecha_txn);

        SET v_id_txn = LAST_INSERT_ID();

        SELECT id_asiento INTO v_id_asiento
        FROM asientos_funciones
        WHERE id_funcion = v_id_func AND estado = 'Disponible'
        ORDER BY id_asiento
        LIMIT 1;

        IF v_id_asiento IS NOT NULL THEN
            UPDATE asientos_funciones SET estado = 'Ocupado'
            WHERE id_funcion = v_id_func AND id_asiento = v_id_asiento;

            INSERT INTO detalle_boleta_asientos (id_transaccion, id_asiento, ingresado)
            VALUES (v_id_txn, v_id_asiento, FALSE);
        END IF;

        INSERT INTO detalle_boleta_confiteria (id_transaccion, id_producto, cantidad, precio_unitario)
        VALUES (v_id_txn, v_id_producto, 1, v_monto_confi);

        INSERT INTO boletas_tickets (id_transaccion, codigo_qr_token, estado_ticket)
        VALUES (v_id_txn, CONCAT('QR-FILMATE-TXN', v_id_txn, '-D', v_idx_dia + 2), 'Valido');

        SET v_idx_iter = v_idx_iter + 1;
    END LOOP read_loop;

    CLOSE cur_funciones;
END //

DELIMITER ;

-- 12 transacciones por día entre el 02/06/2026 y el 14/06/2026 (156 en total)
CALL pr_simular_compras_por_dia('2026-06-02', '2026-06-14', 12);

DROP PROCEDURE IF EXISTS pr_simular_compras_por_dia;


-- ====================================================================
-- COMPONENTE 4: CONSULTAS AVANZADAS, VISTAS Y PROCEDIMIENTOS DE NEGOCIO
-- ====================================================================

USE filmate_db;

-- 4.1. VISTAS CONFIGURADAS PARA FILTRAR BAJAS LÓGICAS (SOFT DELETE)

-- Vista 1: Cartelera Activa Detallada (Filtra películas, cines y salas eliminados)
CREATE OR REPLACE VIEW vw_cartelera_activa AS
SELECT 
    f.id_funcion,
    p.id_pelicula,
    p.titulo AS pelicula_titulo,
    p.duracion_minutos,
    p.clasificacion,
    p.url_poster,
    p.url_trailer,
    c.id_cine,
    c.nombre_cine,
    s.id_sala,
    s.nombre_sala,
    s.tipo_sala,
    s.tipo_formato,
    f.fecha_hora,
    f.precio_base
FROM funciones f
INNER JOIN peliculas p ON f.id_pelicula = p.id_pelicula AND p.eliminado = FALSE
INNER JOIN salas s ON f.id_sala = s.id_sala AND s.eliminado = FALSE
INNER JOIN cines c ON s.id_cine = c.id_cine AND c.eliminado = FALSE
WHERE f.fecha_hora >= NOW()
ORDER BY f.fecha_hora ASC;

-- Vista 2: Métricas de Recaudación por Cine (Ignora cines eliminados)
CREATE OR REPLACE VIEW vw_reporte_ventas_cines AS
SELECT 
    c.id_cine,
    c.nombre_cine,
    COUNT(DISTINCT t.id_transaccion) AS total_transacciones_aprobadas,
    IFNULL(SUM(t.monto_boletos), 0.00) AS ingresos_taquilla,
    IFNULL(SUM(t.monto_confiteria), 0.00) AS ingresos_dulceria,
    IFNULL(SUM(t.monto_total), 0.00) AS recaudacion_total
FROM cines c
LEFT JOIN salas s ON c.id_cine = s.id_cine AND s.eliminado = FALSE
LEFT JOIN funciones f ON s.id_sala = f.id_sala
LEFT JOIN transacciones t ON f.id_funcion = t.id_funcion AND t.estado_pago = 'Aprobado'
WHERE c.eliminado = FALSE
GROUP BY c.id_cine, c.nombre_cine;

-- Vista 3: Feed Social de Reseñas (Oculta contenido de usuarios o películas eliminadas)
CREATE OR REPLACE VIEW vw_feed_social_resenas AS
SELECT 
    r.id_resena,
    u.id_usuario,
    u.username,
    u.url_perfil AS usuario_avatar,
    p.id_pelicula,
    p.titulo AS pelicula_titulo,
    r.puntuacion_estrellas,
    r.comentario,
    r.fecha_publicacion
FROM resenas r
INNER JOIN usuarios u ON r.id_usuario = u.id_usuario AND u.eliminado = FALSE
INNER JOIN peliculas p ON r.id_pelicula = p.id_pelicula AND p.eliminado = FALSE
ORDER BY r.fecha_publicacion DESC;


-- ====================================================================
-- 4.2. PROCEDIMIENTOS ALMACENADOS AVANZADOS (INCLUYE BAJA LÓGICA)
-- ====================================================================
DELIMITER //

-- Procedimiento 1: Soft Delete Cascada para Cines y sus Salas/Asientos
DROP PROCEDURE IF EXISTS pr_eliminar_cine_logico //
CREATE PROCEDURE pr_eliminar_cine_logico(IN p_id_cine INT)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error en cascada de Soft Delete. Operación revertida.';
    END;

    START TRANSACTION;
        -- 1. Marcar baja del Cine
        UPDATE cines SET eliminado = TRUE, fecha_eliminacion = NOW() WHERE id_cine = p_id_cine;
        
        -- 2. Marcar baja de las Salas vinculadas
        UPDATE salas SET eliminado = TRUE, fecha_eliminacion = NOW() WHERE id_cine = p_id_cine;
        
        -- 3. Marcar baja de los Asientos vinculados a las salas de ese cine
        UPDATE asientos a
        INNER JOIN salas s ON a.id_sala = s.id_sala
        SET a.eliminado = TRUE, a.fecha_eliminacion = NOW()
        WHERE s.id_cine = p_id_cine;
    COMMIT;
END //

-- Procedimiento 2: Compra Atómica y Asignación Pesimista de Butacas
DROP PROCEDURE IF EXISTS pr_registrar_compra_boleto //
CREATE PROCEDURE pr_registrar_compra_boleto(
    IN p_id_usuario INT,
    IN p_id_funcion INT,
    IN p_id_asiento INT,
    IN p_monto_boletos DECIMAL(10,2),
    IN p_metodo_pago VARCHAR(50),
    IN p_token_qr VARCHAR(255)
)
BEGIN
    DECLARE v_id_txn INT;
    DECLARE v_estado_asiento VARCHAR(20);
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error transaccional. Proceso de pago abortado.';
    END;

    START TRANSACTION;
    
    SELECT estado INTO v_estado_asiento 
    FROM asientos_funciones 
    WHERE id_funcion = p_id_funcion AND id_asiento = p_id_asiento FOR UPDATE;
    
    IF v_estado_asiento != 'Disponible' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Error: La butaca seleccionada ya no se encuentra libre.';
    ELSE
        UPDATE asientos_funciones SET estado = 'Ocupado' WHERE id_funcion = p_id_funcion AND id_asiento = p_id_asiento;
        
        INSERT INTO transacciones (id_usuario, id_funcion, monto_boletos, monto_confiteria, monto_total, estado_pago, metodo_pago)
        VALUES (p_id_usuario, p_id_funcion, p_monto_boletos, 0.00, p_monto_boletos, 'Aprobado', p_metodo_pago);
        
        SET v_id_txn = LAST_INSERT_ID();
        
        INSERT INTO detalle_boleta_asientos (id_transaccion, id_asiento, ingresado) VALUES (v_id_txn, p_id_asiento, FALSE);
        INSERT INTO boletas_tickets (id_transaccion, codigo_qr_token, estado_ticket) VALUES (v_id_txn, p_token_qr, 'Valido');
    END IF;

    COMMIT;
END //

-- Procedimiento 3: Validación e Ingreso Móvil QR en Puerta
DROP PROCEDURE IF EXISTS pr_validar_ingreso_qr //
CREATE PROCEDURE pr_validar_ingreso_qr(IN p_token_qr VARCHAR(255), IN p_id_portero INT)
BEGIN
    DECLARE v_id_ticket INT;
    DECLARE v_estado_ticket VARCHAR(20);
    DECLARE v_id_txn INT;
    DECLARE v_id_asiento INT;
    DECLARE v_ya_ingresado BOOLEAN;

    SELECT id_ticket, estado_ticket, id_transaccion 
    INTO v_id_ticket, v_estado_ticket, v_id_txn
    FROM boletas_tickets WHERE codigo_qr_token = p_token_qr;

    IF v_id_ticket IS NULL THEN
        INSERT INTO log_validaciones_qr (ticket_escaneado, resultado_validacion, id_usuario_control) VALUES (p_token_qr, 'Inválida', p_id_portero);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'QR Inválido: Entrada no registrada.';
    ELSEIF v_estado_ticket != 'Valido' THEN
        INSERT INTO log_validaciones_qr (ticket_escaneado, resultado_validacion, id_usuario_control) VALUES (p_token_qr, 'Ya Usada', p_id_portero);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Acceso denegado: El ticket ya fue canjeado o anulado.';
    ELSE
        SELECT id_asiento, ingresado INTO v_id_asiento, v_ya_ingresado FROM detalle_boleta_asientos WHERE id_transaccion = v_id_txn LIMIT 1;
        
        IF v_ya_ingresado = TRUE THEN
            INSERT INTO log_validaciones_qr (ticket_escaneado, resultado_validacion, id_usuario_control) VALUES (p_token_qr, 'Ya Usada', p_id_portero);
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Fraude: Esta butaca ya registra ingreso físico activo.';
        ELSE
            UPDATE detalle_boleta_asientos SET ingresado = TRUE, fecha_ingreso = CURRENT_TIMESTAMP WHERE id_transaccion = v_id_txn AND id_asiento = v_id_asiento;
            UPDATE boletas_tickets SET estado_ticket = 'Canjeado' WHERE id_ticket = v_id_ticket;
            INSERT INTO log_validaciones_qr (ticket_escaneado, resultado_validacion, id_usuario_control) VALUES (p_token_qr, 'Valida', p_id_portero);
        END IF;
    END IF;
END //

-- Procedimiento 4: Limpieza Automática de Bloqueos Expirados de Butacas
DROP PROCEDURE IF EXISTS pr_limpiar_bloqueos_expirados //
CREATE PROCEDURE pr_limpiar_bloqueos_expirados()
BEGIN
    UPDATE asientos_funciones af
    INNER JOIN bloqueos_temporales bt ON af.id_funcion = bt.id_funcion AND af.id_asiento = bt.id_asiento
    SET af.estado = 'Disponible' WHERE bt.expira_en < NOW();
    
    DELETE FROM bloqueos_temporales WHERE expira_en < NOW();
END //

DELIMITER ;

-- ====================================================================
-- 4.3. DISPARADORES AUTOMÁTICOS DE AUDITORÍA Y CONTROL DE STOCK
-- ====================================================================
DELIMITER //

-- Trigger 1: Registro Automatizado en Bitácora Social (Reseñas)
DROP TRIGGER IF EXISTS despues_de_publicar_resena //
CREATE TRIGGER despues_de_publicar_resena
AFTER INSERT ON resenas
FOR EACH ROW
BEGIN
    INSERT INTO historial_actividad (id_usuario, tipo_evento, id_referencia_pelicula, id_referencia_resena, texto_breve)
    VALUES (NEW.id_usuario, 'RESENA', NEW.id_pelicula, NEW.id_resena, NEW.comentario);
END //

-- Trigger 2: Contadores Dinámicos de Comunidad e Interacciones (Vistas / Favoritos)
DROP TRIGGER IF EXISTS despues_de_actualizar_interaccion //
CREATE TRIGGER despues_de_actualizar_interaccion
AFTER UPDATE ON interacciones_peliculas
FOR EACH ROW
BEGIN
    IF NEW.favorita = TRUE AND OLD.favorita = FALSE THEN
        UPDATE peliculas SET total_favoritos_comunidad = total_favoritos_comunidad + 1 WHERE id_pelicula = NEW.id_pelicula;
        INSERT INTO historial_actividad (id_usuario, tipo_evento, id_referencia_pelicula, texto_breve)
        VALUES (NEW.id_usuario, 'FAVORITO', NEW.id_pelicula, 'Agregó la película a su lista de favoritos.');
    ELSEIF NEW.favorita = FALSE AND OLD.favorita = TRUE THEN
        UPDATE peliculas SET total_favoritos_comunidad = GREATEST(0, total_favoritos_comunidad - 1) WHERE id_pelicula = NEW.id_pelicula;
    END IF;

    IF NEW.vista = TRUE AND OLD.vista = FALSE THEN
        UPDATE peliculas SET total_vistas_comunidad = total_vistas_comunidad + 1 WHERE id_pelicula = NEW.id_pelicula;
    END IF;
END //

-- Trigger 3: Descuento de Inventario Físico Automatizado al Vender Dulcería
DROP TRIGGER IF EXISTS despues_de_vender_confiteria //
CREATE TRIGGER despues_de_vender_confiteria
AFTER INSERT ON detalle_boleta_confiteria
FOR EACH ROW
BEGIN
    UPDATE productos_confiteria SET stock = GREATEST(0, stock - NEW.cantidad) WHERE id_producto = NEW.id_producto;
END //

-- Trigger 4: Bitácora Social para Nuevos Seguidores
DROP TRIGGER IF EXISTS despues_de_seguir_usuario //
CREATE TRIGGER despues_de_seguir_usuario
AFTER INSERT ON seguidores
FOR EACH ROW
BEGIN
    INSERT INTO historial_actividad (id_usuario, tipo_evento, id_referencia_usuario, texto_breve)
    VALUES (NEW.id_seguidor, 'SEGUIDOR', NEW.id_seguido, 'Comenzó a seguir a un miembro de la comunidad.');
END //

-- Trigger 5: Alerta de Auditoría Interna ante Alteración de Precios de Funciones
DROP TRIGGER IF EXISTS auditoria_alteracion_precios //
CREATE TRIGGER auditoria_alteracion_precios
AFTER UPDATE ON funciones
FOR EACH ROW
BEGIN
    IF OLD.precio_base <> NEW.precio_base THEN
        INSERT INTO log_actividad_sistema (id_usuario, accion_realizada, modulo_afectado, ip_origen)
        VALUES (NULL, CONCAT('Cambio de precio base en función ID: ', NEW.id_funcion, '. Anterior: S/.', OLD.precio_base, ' -> Nuevo: S/.', NEW.precio_base), 'CARTELERA', '127.0.0.1');
    END IF;
END //

DELIMITER ;