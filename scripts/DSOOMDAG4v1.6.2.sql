-- =========================================================
-- LIMPIAR Y CREAR BASE DE DATOS
-- =========================================================

DROP DATABASE IF EXISTS filmate_db;

CREATE DATABASE filmate_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE filmate_db;

-- =========================================================
-- TABLAS
-- =========================================================

-- 1. SEGURIDAD Y USUARIOS

CREATE TABLE rol (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    id_rol INT NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    estado ENUM('Activo', 'Bloqueado', 'Inactivo') DEFAULT 'Activo',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
);

-- 2. PELICULAS Y CATALOGO

CREATE TABLE pelicula (
    id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    sinopsis TEXT,
    duracion_minutos INT,
    clasificacion_edad VARCHAR(10),
    url_poster VARCHAR(500),
    url_trailer VARCHAR(500),
    url_banner VARCHAR(500),
    categoria_cartelera ENUM('Estreno', 'Preventa', 'Cartelera', 'Proximamente') DEFAULT 'Proximamente',
    estado_registro ENUM('Activo', 'Inactivo') DEFAULT 'Activo',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE genero (
    id_genero INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE pelicula_genero (
    id_pelicula INT NOT NULL,
    id_genero INT NOT NULL,
    PRIMARY KEY (id_pelicula, id_genero),
    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_genero) REFERENCES genero(id_genero) ON DELETE CASCADE
);

CREATE TABLE actor (
    id_actor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE pelicula_actor (
    id_pelicula INT NOT NULL,
    id_actor INT NOT NULL,
    personaje VARCHAR(100) NOT NULL,
    PRIMARY KEY (id_pelicula, id_actor),
    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_actor) REFERENCES actor(id_actor) ON DELETE CASCADE
);

CREATE TABLE banner_home (
    id_banner INT AUTO_INCREMENT PRIMARY KEY,
    id_pelicula INT,
    imagen_url VARCHAR(500) NOT NULL,
    orden INT NOT NULL,
    is_activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula)
);

-- 3. COMUNIDAD

CREATE TABLE resena (
    id_resena INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_pelicula INT NOT NULL,
    calificacion_estrellas DECIMAL(2,1),
    comentario TEXT,
    estado_moderacion ENUM('Aprobado', 'Pendiente', 'Oculto') DEFAULT 'Aprobado',
    fecha_publicacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula),
    CHECK (calificacion_estrellas BETWEEN 1 AND 5)
);

CREATE TABLE favorito (
    id_usuario INT NOT NULL,
    id_pelicula INT NOT NULL,
    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_pelicula),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula) ON DELETE CASCADE
);

-- 4. CINES

CREATE TABLE cine (
    id_cine INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    estado BOOLEAN DEFAULT TRUE
);

CREATE TABLE sala (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    id_cine INT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    formato_sala VARCHAR(20),
    capacidad_total INT NOT NULL,
    FOREIGN KEY (id_cine) REFERENCES cine(id_cine)
);

CREATE TABLE asiento (
    id_asiento INT AUTO_INCREMENT PRIMARY KEY,
    id_sala INT NOT NULL,
    fila VARCHAR(5) NOT NULL,
    numero INT NOT NULL,
    coord_x INT,
    coord_y INT,
    estado_fisico ENUM('Disponible', 'Mantenimiento', 'Inhabilitado') DEFAULT 'Disponible',
    FOREIGN KEY (id_sala) REFERENCES sala(id_sala),
    UNIQUE (id_sala, fila, numero)
);

-- 5. FUNCIONES

CREATE TABLE funcion (
    id_funcion INT AUTO_INCREMENT PRIMARY KEY,
    id_pelicula INT NOT NULL,
    id_sala INT NOT NULL,
    fecha_hora_inicio DATETIME NOT NULL,
    fecha_hora_fin DATETIME NOT NULL,
    idioma VARCHAR(50),
    formato VARCHAR(20),
    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula),
    FOREIGN KEY (id_sala) REFERENCES sala(id_sala)
);

CREATE TABLE funcion_asiento (
    id_funcion INT NOT NULL,
    id_asiento INT NOT NULL,
    estado ENUM('Disponible', 'Reservado', 'Vendido') DEFAULT 'Disponible',
    PRIMARY KEY (id_funcion, id_asiento),
    FOREIGN KEY (id_funcion) REFERENCES funcion(id_funcion) ON DELETE CASCADE,
    FOREIGN KEY (id_asiento) REFERENCES asiento(id_asiento) ON DELETE CASCADE
);

CREATE TABLE tarifa (
    id_tarifa INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    precio DECIMAL(8,2) NOT NULL,
    dia_aplica ENUM(
        'Lunes',
        'Martes',
        'Miercoles',
        'Jueves',
        'Viernes',
        'Sabado',
        'Domingo',
        'Todos'
    ) DEFAULT 'Todos'
);

CREATE TABLE promocion (
    id_promocion INT AUTO_INCREMENT PRIMARY KEY,
    codigo_cupon VARCHAR(20) UNIQUE NOT NULL,
    porcentaje_descuento DECIMAL(5,2),
    monto_descuento DECIMAL(8,2),
    fecha_inicio DATETIME,
    fecha_fin DATETIME,
    limite_usos INT
);

-- 6. RESERVAS

CREATE TABLE reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_funcion INT NOT NULL,
    id_promocion INT NULL,
    fecha_reserva DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion DATETIME NOT NULL,
    monto_subtotal DECIMAL(10,2) NOT NULL,
    descuento_aplicado DECIMAL(10,2) DEFAULT 0.00,
    monto_total DECIMAL(10,2) NOT NULL,
    estado_pago ENUM('Pendiente', 'Pagado', 'Cancelado', 'Reembolsado') DEFAULT 'Pendiente',
    metodo_pago VARCHAR(50),
    transaccion_id VARCHAR(100),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_funcion) REFERENCES funcion(id_funcion),
    FOREIGN KEY (id_promocion) REFERENCES promocion(id_promocion)
);

CREATE TABLE boleto (
    id_boleto INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva INT NOT NULL,
    id_funcion INT NOT NULL,
    id_asiento INT NOT NULL,
    id_tarifa INT NOT NULL,
    codigo_qr VARCHAR(255) UNIQUE NOT NULL,
    precio_pagado DECIMAL(8,2) NOT NULL,
    estado_ingreso ENUM('Vigente', 'Usado') DEFAULT 'Vigente',
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva),
    FOREIGN KEY (id_funcion) REFERENCES funcion(id_funcion),
    FOREIGN KEY (id_asiento) REFERENCES asiento(id_asiento),
    FOREIGN KEY (id_tarifa) REFERENCES tarifa(id_tarifa),
    UNIQUE (id_funcion, id_asiento)
);

-- 7. SNACKS

CREATE TABLE categoria_snack (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    orden_visual INT NOT NULL DEFAULT 0,
    estado BOOLEAN DEFAULT TRUE
);

CREATE TABLE producto_snack (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    precio_actual DECIMAL(8,2) NOT NULL,
    url_imagen VARCHAR(500) NOT NULL,
    is_activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_categoria) REFERENCES categoria_snack(id_categoria) ON DELETE CASCADE
);

CREATE TABLE reserva_snack (
    id_reserva INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(8,2) NOT NULL,
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    PRIMARY KEY (id_reserva, id_producto),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES producto_snack(id_producto),
    CHECK (cantidad > 0)
);

-- =========================================================
-- INDICES
-- =========================================================

CREATE INDEX idx_funcion_fecha ON funcion(fecha_hora_inicio);
CREATE INDEX idx_resena_pelicula ON resena(id_pelicula);
CREATE INDEX idx_reserva_usuario ON reserva(id_usuario);

-- =========================================================
-- DATOS
-- =========================================================

-- ============================================================
--  FILMATE_DB — SCRIPT DE DATOS DE PRUEBA
--  Basado en el schema de filmate_db (script 1)
--  Datos adaptados del script 2
-- ============================================================

USE filmate_db;

-- ============================================================
-- 1. ROLES
-- ============================================================
INSERT INTO rol (id_rol, nombre) VALUES
(1, 'Admin'),
(2, 'Cliente');

-- ============================================================
-- 2. USUARIOS (2 Admins + 28 Clientes)
-- ============================================================
INSERT INTO usuario (id_rol, nombres, apellidos, correo, password_hash, estado, fecha_registro) VALUES
(1, 'Carlos',    'Mendoza',    'carlos.mendoza@filmate.pe',  '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-01-05 09:00:00'),
(1, 'Valeria',   'Torres',     'valeria.torres@filmate.pe',  '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-01-06 10:00:00'),
(2, 'Andrés',    'Quispe',     'andres.quispe@gmail.com',    '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-02-10 14:23:00'),
(2, 'Lucía',     'Paredes',    'lucia.paredes@gmail.com',    '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-02-11 09:45:00'),
(2, 'Miguel',    'Ramos',      'miguel.ramos@hotmail.com',   '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-02-12 16:30:00'),
(2, 'Sofía',     'Gutierrez',  'sofia.gutierrez@gmail.com',  '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-03-01 11:00:00'),
(2, 'Diego',     'Llanos',     'diego.llanos@yahoo.com',     '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-03-03 08:15:00'),
(2, 'Camila',    'Flores',     'camila.flores@gmail.com',    '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-03-05 19:20:00'),
(2, 'Rodrigo',   'Salinas',    'rodrigo.salinas@gmail.com',  '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-03-07 12:00:00'),
(2, 'Natalia',   'Vega',       'natalia.vega@gmail.com',     '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-03-10 10:30:00'),
(2, 'Sebastián', 'Castro',     'sebastian.castro@gmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-04-01 14:00:00'),
(2, 'Fernanda',  'Moran',      'fernanda.moran@gmail.com',   '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Bloqueado','2026-04-05 09:00:00'),
(2, 'Jorge',     'Huanca',     'jorge.huanca@hotmail.com',   '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-04-08 17:45:00'),
(2, 'Paola',     'Rios',       'paola.rios@gmail.com',       '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-04-10 13:20:00'),
(2, 'Ivan',      'Mamani',     'ivan.mamani@gmail.com',      '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-04-15 08:00:00'),
(2, 'Claudia',   'Rueda',      'claudia.rueda@gmail.com',    '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-04-20 11:30:00'),
(2, 'Erick',     'Soto',       'erick.soto@gmail.com',       '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-05-01 16:00:00'),
(2, 'Daniela',   'Lara',       'daniela.lara@gmail.com',     '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-05-03 10:00:00'),
(2, 'Alejandro', 'Vargas',     'alejandro.vargas@gmail.com', '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-05-05 12:45:00'),
(2, 'Mariana',   'Delgado',    'mariana.delgado@gmail.com',  '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-05-10 09:20:00'),
(2, 'Paul',      'Condori',    'paul.condori@gmail.com',     '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-05-15 14:00:00'),
(2, 'Kiara',     'Reyes',      'kiara.reyes@gmail.com',      '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-05-20 16:30:00'),
(2, 'Omar',      'Salas',      'omar.salas@yahoo.com',       '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Inactivo', '2026-06-01 11:00:00'),
(2, 'Brenda',    'Chávez',     'brenda.chavez@gmail.com',    '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-06-05 09:30:00'),
(2, 'Lenin',     'Huamán',     'lenin.huaman@gmail.com',     '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-06-10 10:00:00'),
(2, 'Rosa',      'Apaza',      'rosa.apaza@gmail.com',       '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-06-15 08:45:00'),
(2, 'Jhon',      'Zuñiga',     'jhon.zuniga@gmail.com',      '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-07-01 13:00:00'),
(2, 'Ariana',    'Paz',        'ariana.paz@gmail.com',       '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-07-05 15:00:00'),
(2, 'Marco',     'Vilca',      'marco.vilca@gmail.com',      '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-07-10 12:00:00'),
(2, 'Yesenia',   'Ticona',     'yesenia.ticona@gmail.com',   '/PeNCKLdvd25DOginwCXdXpBCDBTDUsw2icHmh6cvsDVYjm2NNQyMfp7M8tsvUNN', 'Activo',   '2026-07-15 17:00:00');
-- ============================================================
-- 3. GÉNEROS
-- ============================================================
INSERT INTO genero (id_genero, nombre) VALUES
(1,  'Accion'),
(2,  'Aventura'),
(3,  'Animacion'),
(4,  'Comedia'),
(5,  'Crimen'),
(6,  'Drama'),
(7,  'Terror'),
(8,  'Ciencia Ficcion'),
(9,  'Thriller'),
(10, 'Romance'),
(11, 'Fantasia'),
(12, 'Misterio'),
(13, 'Musical'),
(14, 'Belica'),
(15, 'Documental'),
(16, 'Superheroes'),
(17, 'Familiar');

-- ============================================================
-- 4. PELÍCULAS (20 películas)
-- ============================================================
INSERT INTO pelicula (id_pelicula, titulo, sinopsis, duracion_minutos, clasificacion_edad, url_poster, url_trailer, url_banner, categoria_cartelera, estado_registro) VALUES

(1, 'Dune: Parte Dos',
 'Paul Atreides se une a los Fremen y busca venganza contra los conspiradores que destruyeron a su familia mientras intenta evitar el futuro que solo él puede predecir.',
 166, '+14',
 'https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg',
 'https://www.youtube.com/embed/Way9Dexny3w',
 'https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s5hj0PX.jpg',
 'Estreno', 'Activo'),

(2, 'Deadpool & Wolverine',
 'Wade Wilson sale del retiro para unirse a Wolverine en una misión que cambiará la historia del Universo Marvel.',
 128, '+14',
 'https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg',
 'https://www.youtube.com/embed/73_1biulkYk',
 'https://image.tmdb.org/t/p/original/30YacPAcxpNemhhwX667IABLIAk.jpg',
 'Estreno', 'Activo'),

(3, 'Inside Out 2',
 'Riley enfrenta la adolescencia cuando nuevas emociones — incluyendo Ansiedad — irrumpen y complican todo.',
 100, 'APT',
 'https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg',
 'https://www.youtube.com/embed/LEjhY15eCx0',
 'https://image.tmdb.org/t/p/original/4HodYYKEIsGOdinkGi2Ucz6X9i0.jpg',
 'Cartelera', 'Activo'),

(4, 'Alien: Romulus',
 'Un grupo de jóvenes colonos espaciales se enfrenta a la forma de vida más aterradora del universo mientras explora las ruinas de una estación espacial abandonada.',
 119, '+18',
 'https://image.tmdb.org/t/p/w500/b33nnKl1GSFbao4l3fZDDqsMx0F.jpg',
 'https://www.youtube.com/embed/5nWH2Pd-x-c',
 'https://image.tmdb.org/t/p/original/b33nnKl1GSFbao4l3fZDDqsMx0F.jpg',
 'Cartelera', 'Activo'),

(5, 'Oppenheimer',
 'La historia de J. Robert Oppenheimer y su papel en el desarrollo de la primera bomba atómica durante la Segunda Guerra Mundial.',
 180, '+14',
 'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg',
 'https://www.youtube.com/embed/uYPbbksJxIg',
 'https://image.tmdb.org/t/p/original/rLb2cwF3Pazuxaj0sRXQ037tGI1.jpg',
 'Cartelera', 'Activo'),

(6, 'Kung Fu Panda 4',
 'Po debe entrenar a un nuevo guerrero dragón y enfrentar a una villana con el poder de invocar a los enemigos del pasado.',
 94, 'APT',
 'https://image.tmdb.org/t/p/w500/kDp1vUBnMpe8ak4rjgl3cLELqjU.jpg',
 'https://www.youtube.com/embed/kg3Q63gzF6I',
 'https://image.tmdb.org/t/p/original/kDp1vUBnMpe8ak4rjgl3cLELqjU.jpg',
 'Cartelera', 'Activo'),

(7, 'Gladiador II',
 'Lucio, sobrino del fallecido Máximo, lucha en el Coliseo romano mientras los tiranos Geta y Caracala gobiernan el Imperio.',
 148, '+14',
 'https://image.tmdb.org/t/p/w500/2cxhvwyEwRlysAmRH4iodkvo0z5.jpg',
 'https://www.youtube.com/embed/ZEJgVq1K8S4',
 'https://image.tmdb.org/t/p/original/tkFE9oi7iBMBSWLYHoQMfWyFi1Q.jpg',
 'Estreno', 'Activo'),

(8, 'Wicked',
 'La historia no contada de las brujas de Oz: cómo la amistad entre Elphaba y Glinda fue transformada por traición y poder.',
 160, 'APT',
 'https://image.tmdb.org/t/p/w500/xDGbZ0JJ3mYaGKy4Nzd9Kph6M9L.jpg',
 'https://www.youtube.com/embed/JDSRDbFqc_E',
 'https://image.tmdb.org/t/p/original/rBOOfRfZsS7mAEFKKzMQQMFNUmQ.jpg',
 'Estreno', 'Activo'),

(9, 'Moana 2',
 'Moana emprende un nuevo viaje a los mares ancestrales de Oceanía tras recibir un llamado inesperado de sus ancestros.',
 100, 'APT',
 'https://lumiere-a.akamaihd.net/v1/images/image_25b12a37.jpeg?region=0%2C0%2C540%2C810',
 'https://www.youtube.com/embed/hDZ7y8RP5HE',
 'https://image.tmdb.org/t/p/original/aLVkiINlIeCkCJIqeHZjN988eqp.jpg',
 'Proximamente', 'Activo'),

(10, 'Venom: El Último Baile',
 'Eddie Brock y Venom se ven obligados a tomar una decisión devastadora cuando una nueva amenaza acecha sus vidas.',
 109, '+14',
 'https://image.tmdb.org/t/p/w500/aosm8NMQ3UyoBVpSxyimorCQykC.jpg',
 'https://www.youtube.com/embed/jcTP9BvoW1o',
 'https://image.tmdb.org/t/p/original/aosm8NMQ3UyoBVpSxyimorCQykC.jpg',
 'Cartelera', 'Activo'),

(11, 'El Señor de los Anillos: La Guerra de los Rohirrim',
 'Precuela animada que narra la épica batalla de Helm''s Deep desde la perspectiva de la Casa de Helm Hammerhand.',
 134, '+14',
 'https://imagenes.hobbyconsolas.com/files/image_990_auto/uploads/imagenes/2024/10/24/6903dbaca1b4c.jpeg',
 'https://www.youtube.com/embed/jrhSLlos5bU',
 'https://image.tmdb.org/t/p/original/r4sRSGEAkuCIBsNr11fDwVOE8nq.jpg',
 'Proximamente', 'Activo'),

(12, 'Joker: Folie à Deux',
 'Arthur Fleck está internado en Arkham esperando su juicio cuando conoce al amor de su vida y descubren la música juntos.',
 138, '+18',
 'https://imagenes.hobbyconsolas.com/files/image_990_auto/uploads/imagenes/2024/04/02/6903aebb9f764.jpeg',
 'https://www.youtube.com/embed/spAv-FNhOvA',
 'https://image.tmdb.org/t/p/original/hS0x0sFM1GjBBq1GVmU6n9d8awr.jpg',
 'Cartelera', 'Activo'),

(13, 'Twisters',
 'Una ex cazadora de tornados regresa al campo para probar una técnica revolucionaria para detener los tornados en el corazón de la Tornado Alley.',
 122, '+7',
 'https://www.movieposters.com/cdn/shop/files/twisters_ver2.jpg?v=1762976527&width=1680',
 'https://www.youtube.com/embed/wdok0rZdmx4',
 'https://image.tmdb.org/t/p/original/pjnD08FlMAIXsfOLKQbovhFyiav.jpg',
 'Cartelera', 'Activo'),

(14, 'Beetlejuice Beetlejuice',
 'Después de una tragedia familiar, Lydia Deetz regresa a Winter River con su hija adolescente, donde su pasado sobrenatural la alcanza.',
 104, '+14',
 'https://image.tmdb.org/t/p/w500/kKgQzkUCnQmeTPkyIwHly2t6ZFI.jpg',
 'https://www.youtube.com/embed/CoZqL9N6Rx4',
 'https://image.tmdb.org/t/p/original/kKgQzkUCnQmeTPkyIwHly2t6ZFI.jpg',
 'Cartelera', 'Activo'),

(15, 'Terrifier 3',
 'Art el Payaso regresa para sembrar el caos y el terror durante la temporada navideña, marcando un nuevo nivel de brutalidad.',
 125, '+18',
 'https://image.tmdb.org/t/p/w500/l1175hgL5DoXnqeZQCcU3eZIdhX.jpg',
 'https://www.youtube.com/embed/Y2u6m2W428g',
 'https://image.tmdb.org/t/p/original/l1175hgL5DoXnqeZQCcU3eZIdhX.jpg',
 'Cartelera', 'Activo'),

(16, 'Aquaman y el Reino Perdido',
 'Arthur Curry recurre a un aliado improbable para proteger Atlantis cuando una antigua fuerza oscura amenaza con destruir el mundo.',
 124, '+7',
 'https://image.tmdb.org/t/p/w500/7lTnXOy0iNtBAdRP3TZvaKJ77F6.jpg',
 'https://www.youtube.com/embed/M8W_y0mmJEc',
 'https://image.tmdb.org/t/p/original/7lTnXOy0iNtBAdRP3TZvaKJ77F6.jpg',
 'Cartelera', 'Activo'),

(17, 'The Batman',
 'En el segundo año de Batman en Gotham, un asesino en serie expone la corrupción de la élite de la ciudad a través de crueles acertijos.',
 176, '+14',
 'https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg',
 'https://www.youtube.com/embed/mqqft2x_Aa4',
 'https://image.tmdb.org/t/p/original/74xTEgt7R36Fpooo50r9T25onhq.jpg',
 'Cartelera', 'Activo'),

(18, 'Avatar: El Camino del Agua',
 'Jake Sully y Neytiri forman una familia en Pandora. Cuando una vieja amenaza regresa, deben dejar su hogar y explorar las regiones del océano.',
 192, '+7',
 'https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg',
 'https://www.youtube.com/embed/a8Gx8wiNbs8',
 'https://image.tmdb.org/t/p/original/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg',
 'Cartelera', 'Activo'),

(19, 'Spider-Man: Cruzando el Multiverso',
 'Miles Morales regresa para una aventura épica que lo llevará por el Multiverso, donde se reunirá con Gwen Stacy y un nuevo equipo de Spider-People.',
 140, '+7',
 'https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg',
 'https://www.youtube.com/embed/cqGjhVJWtEg',
 'https://image.tmdb.org/t/p/original/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg',
 'Cartelera', 'Activo'),

(20, 'John Wick 4',
 'John Wick descubre un camino para derrotar a la Alta Mesa. Pero antes de ganar su libertad, debe enfrentarse a un nuevo enemigo con alianzas poderosas.',
 169, '+18',
 'https://image.tmdb.org/t/p/w500/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg',
 'https://www.youtube.com/embed/qEVUtrk8_B4',
 'https://image.tmdb.org/t/p/original/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg',
 'Cartelera', 'Activo');

-- ============================================================
-- 5. RELACIÓN PELÍCULA–GÉNERO
-- ============================================================
INSERT INTO pelicula_genero (id_pelicula, id_genero) VALUES
(1, 8),(1, 2),(1, 6),
(2, 1),(2, 4),(2,16),
(3, 3),(3, 4),(3, 6),
(4, 7),(4, 8),(4, 9),
(5, 6),(5, 9),(5,14),
(6, 3),(6, 2),(6, 4),
(7, 1),(7, 6),(7, 2),
(8, 6),(8,13),(8,11),
(9, 3),(9, 2),(9,11),
(10,1),(10,8),(10,9),
(11,3),(11,2),(11,11),
(12,5),(12,6),(12,13),
(13,1),(13,2),(13,9),
(14,4),(14,7),(14,11),
(15,7),(15,9),
(16,1),(16,2),(16,16),
(17,1),(17,5),(17,12),
(18,8),(18,2),(18,6),
(19,1),(19,2),(19,3),
(20,1),(20,5),(20,9);

-- ============================================================
-- 6. ACTORES
-- ============================================================
INSERT INTO actor (id_actor, nombre) VALUES
(1,  'Timothée Chalamet'),
(2,  'Zendaya'),
(3,  'Rebecca Ferguson'),
(4,  'Ryan Reynolds'),
(5,  'Hugh Jackman'),
(6,  'Emma Stone'),
(7,  'Amy Poehler'),
(8,  'Maya Hawke'),
(9,  'Cailee Spaeny'),
(10, 'David Jonsson'),
(11, 'Cillian Murphy'),
(12, 'Emily Blunt'),
(13, 'Matt Damon'),
(14, 'Jack Black'),
(15, 'Bryan Cranston'),
(16, 'Paul Mescal'),
(17, 'Pedro Pascal'),
(18, 'Cynthia Erivo'),
(19, 'Ariana Grande'),
(20, 'Auliʻi Cravalho'),
(21, 'Tom Hardy'),
(22, 'Michelle Williams'),
(23, 'Daisy Ridley'),
(24, 'Joaquin Phoenix'),
(25, 'Lady Gaga'),
(26, 'Daisy Edgar-Jones'),
(27, 'Glen Powell'),
(28, 'Michael Keaton'),
(29, 'Winona Ryder'),
(30, 'Robert Pattinson');

-- ============================================================
-- 7. RELACIÓN PELÍCULA–ACTOR
-- ============================================================
INSERT INTO pelicula_actor (id_pelicula, id_actor, personaje) VALUES
(1,  1,  'Paul Atreides'),
(1,  2,  'Chani'),
(1,  3,  'Lady Jessica'),
(2,  4,  'Deadpool / Wade Wilson'),
(2,  5,  'Wolverine / Logan'),
(3,  6,  'Alegría'),
(3,  7,  'Miedo'),
(3,  8,  'Ansiedad'),
(4,  9,  'Rain'),
(4,  10, 'Andy'),
(5,  11, 'J. Robert Oppenheimer'),
(5,  12, 'Katherine Oppenheimer'),
(5,  13, 'Matt'),
(6,  14, 'Po'),
(6,  15, 'Mr. Ping'),
(7,  16, 'Lucio'),
(7,  17, 'Marcus Acacius'),
(8,  18, 'Elphaba'),
(8,  19, 'Glinda'),
(9,  20, 'Moana'),
(10, 21, 'Eddie Brock / Venom'),
(10, 22, 'Anne Weying'),
(12, 24, 'Arthur Fleck / Joker'),
(12, 25, 'Lee Quinzel / Harley Quinn'),
(13, 26, 'Kate Cooper'),
(13, 27, 'Tyler Owens'),
(14, 28, 'Betelgeuse'),
(14, 29, 'Lydia Deetz'),
(17, 30, 'Bruce Wayne / Batman'),
(20, 1,  'John Wick');

-- ============================================================
-- 8. BANNERS HOME
-- ============================================================
INSERT INTO banner_home (id_pelicula, imagen_url, orden, is_activo) VALUES
(1,  'https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s5hj0PX.jpg', 1, TRUE),
(2,  'https://image.tmdb.org/t/p/original/30YacPAcxpNemhhwX667IABLIAk.jpg', 2, TRUE),
(7,  'https://image.tmdb.org/t/p/original/tkFE9oi7iBMBSWLYHoQMfWyFi1Q.jpg', 3, TRUE),
(8,  'https://image.tmdb.org/t/p/original/rBOOfRfZsS7mAEFKKzMQQMFNUmQ.jpg', 4, TRUE),
(19, 'https://image.tmdb.org/t/p/original/4HodYYKEIsGOdinkGi2Ucz6X9i0.jpg', 5, TRUE),
(5,  'https://image.tmdb.org/t/p/original/rLb2cwF3Pazuxaj0sRXQ037tGI1.jpg', 6, FALSE);

-- ============================================================
-- 9. CINES
-- ============================================================
INSERT INTO cine (id_cine, nombre, direccion, ciudad, estado) VALUES
(1, 'Filmate Miraflores', 'Av. Larco 1036, Miraflores',           'Lima', TRUE),
(2, 'Filmate San Isidro', 'Av. Conquistadores 511, San Isidro',   'Lima', TRUE),
(3, 'Filmate La Molina',  'Av. La Molina 1300, La Molina',        'Lima', TRUE),
(4, 'Filmate Surco',      'Av. Primavera 2390, Santiago de Surco','Lima', TRUE);

-- ============================================================
-- 10. SALAS
-- ============================================================
INSERT INTO sala (id_sala, id_cine, nombre, formato_sala, capacidad_total) VALUES
(1,  1, 'Sala 1 - IMAX', 'IMAX', 200),
(2,  1, 'Sala 2 - 4DX',  '4DX',  100),
(3,  1, 'Sala 3 - 2D',   '2D',   150),
(4,  2, 'Sala 1 - IMAX', 'IMAX', 200),
(5,  2, 'Sala 2 - 3D',   '3D',   120),
(6,  2, 'Sala 3 - 2D',   '2D',   150),
(7,  3, 'Sala 1 - 3D',   '3D',   130),
(8,  3, 'Sala 2 - 2D',   '2D',   140),
(9,  3, 'Sala 3 - 4DX',  '4DX',   90),
(10, 4, 'Sala 1 - IMAX', 'IMAX', 210),
(11, 4, 'Sala 2 - 3D',   '3D',   110),
(12, 4, 'Sala 3 - 2D',   '2D',   160);

-- ============================================================
-- 11. ASIENTOS
--     Sala 1 (IMAX Miraflores): filas A–J, 10 asientos c/u = 100
--     Sala 2 (4DX Miraflores): filas A–E, 8 asientos c/u  =  40
--     Sala 3 (2D Miraflores):  filas A–E, 8 asientos c/u  =  40
-- ============================================================
INSERT INTO asiento (id_sala, fila, numero, coord_x, coord_y, estado_fisico) VALUES
-- SALA 1
(1,'A',1,10,10,'Disponible'),(1,'A',2,60,10,'Disponible'),(1,'A',3,110,10,'Disponible'),(1,'A',4,160,10,'Disponible'),(1,'A',5,210,10,'Disponible'),
(1,'A',6,260,10,'Disponible'),(1,'A',7,310,10,'Disponible'),(1,'A',8,360,10,'Disponible'),(1,'A',9,410,10,'Disponible'),(1,'A',10,460,10,'Disponible'),
(1,'B',1,10,60,'Disponible'),(1,'B',2,60,60,'Disponible'),(1,'B',3,110,60,'Disponible'),(1,'B',4,160,60,'Disponible'),(1,'B',5,210,60,'Disponible'),
(1,'B',6,260,60,'Disponible'),(1,'B',7,310,60,'Disponible'),(1,'B',8,360,60,'Disponible'),(1,'B',9,410,60,'Disponible'),(1,'B',10,460,60,'Disponible'),
(1,'C',1,10,110,'Disponible'),(1,'C',2,60,110,'Disponible'),(1,'C',3,110,110,'Disponible'),(1,'C',4,160,110,'Disponible'),(1,'C',5,210,110,'Disponible'),
(1,'C',6,260,110,'Disponible'),(1,'C',7,310,110,'Disponible'),(1,'C',8,360,110,'Disponible'),(1,'C',9,410,110,'Disponible'),(1,'C',10,460,110,'Disponible'),
(1,'D',1,10,160,'Disponible'),(1,'D',2,60,160,'Disponible'),(1,'D',3,110,160,'Disponible'),(1,'D',4,160,160,'Disponible'),(1,'D',5,210,160,'Disponible'),
(1,'D',6,260,160,'Disponible'),(1,'D',7,310,160,'Disponible'),(1,'D',8,360,160,'Disponible'),(1,'D',9,410,160,'Mantenimiento'),(1,'D',10,460,160,'Disponible'),
(1,'E',1,10,210,'Disponible'),(1,'E',2,60,210,'Disponible'),(1,'E',3,110,210,'Disponible'),(1,'E',4,160,210,'Disponible'),(1,'E',5,210,210,'Disponible'),
(1,'E',6,260,210,'Disponible'),(1,'E',7,310,210,'Disponible'),(1,'E',8,360,210,'Disponible'),(1,'E',9,410,210,'Disponible'),(1,'E',10,460,210,'Disponible'),
(1,'F',1,10,260,'Disponible'),(1,'F',2,60,260,'Disponible'),(1,'F',3,110,260,'Disponible'),(1,'F',4,160,260,'Disponible'),(1,'F',5,210,260,'Disponible'),
(1,'F',6,260,260,'Disponible'),(1,'F',7,310,260,'Disponible'),(1,'F',8,360,260,'Inhabilitado'),(1,'F',9,410,260,'Disponible'),(1,'F',10,460,260,'Disponible'),
(1,'G',1,10,310,'Disponible'),(1,'G',2,60,310,'Disponible'),(1,'G',3,110,310,'Disponible'),(1,'G',4,160,310,'Disponible'),(1,'G',5,210,310,'Disponible'),
(1,'G',6,260,310,'Disponible'),(1,'G',7,310,310,'Disponible'),(1,'G',8,360,310,'Disponible'),(1,'G',9,410,310,'Disponible'),(1,'G',10,460,310,'Disponible'),
(1,'H',1,10,360,'Disponible'),(1,'H',2,60,360,'Disponible'),(1,'H',3,110,360,'Disponible'),(1,'H',4,160,360,'Disponible'),(1,'H',5,210,360,'Disponible'),
(1,'H',6,260,360,'Disponible'),(1,'H',7,310,360,'Disponible'),(1,'H',8,360,360,'Disponible'),(1,'H',9,410,360,'Disponible'),(1,'H',10,460,360,'Disponible'),
(1,'I',1,10,410,'Disponible'),(1,'I',2,60,410,'Disponible'),(1,'I',3,110,410,'Disponible'),(1,'I',4,160,410,'Disponible'),(1,'I',5,210,410,'Disponible'),
(1,'I',6,260,410,'Disponible'),(1,'I',7,310,410,'Disponible'),(1,'I',8,360,410,'Disponible'),(1,'I',9,410,410,'Disponible'),(1,'I',10,460,410,'Disponible'),
(1,'J',1,10,460,'Disponible'),(1,'J',2,60,460,'Disponible'),(1,'J',3,110,460,'Disponible'),(1,'J',4,160,460,'Disponible'),(1,'J',5,210,460,'Disponible'),
(1,'J',6,260,460,'Disponible'),(1,'J',7,310,460,'Disponible'),(1,'J',8,360,460,'Disponible'),(1,'J',9,410,460,'Disponible'),(1,'J',10,460,460,'Disponible'),
-- SALA 2
(2,'A',1,10,10,'Disponible'),(2,'A',2,60,10,'Disponible'),(2,'A',3,110,10,'Disponible'),(2,'A',4,160,10,'Disponible'),(2,'A',5,210,10,'Disponible'),(2,'A',6,260,10,'Disponible'),(2,'A',7,310,10,'Disponible'),(2,'A',8,360,10,'Disponible'),
(2,'B',1,10,60,'Disponible'),(2,'B',2,60,60,'Disponible'),(2,'B',3,110,60,'Disponible'),(2,'B',4,160,60,'Disponible'),(2,'B',5,210,60,'Disponible'),(2,'B',6,260,60,'Disponible'),(2,'B',7,310,60,'Disponible'),(2,'B',8,360,60,'Disponible'),
(2,'C',1,10,110,'Disponible'),(2,'C',2,60,110,'Disponible'),(2,'C',3,110,110,'Disponible'),(2,'C',4,160,110,'Disponible'),(2,'C',5,210,110,'Disponible'),(2,'C',6,260,110,'Disponible'),(2,'C',7,310,110,'Disponible'),(2,'C',8,360,110,'Disponible'),
(2,'D',1,10,160,'Disponible'),(2,'D',2,60,160,'Disponible'),(2,'D',3,110,160,'Disponible'),(2,'D',4,160,160,'Disponible'),(2,'D',5,210,160,'Disponible'),(2,'D',6,260,160,'Disponible'),(2,'D',7,310,160,'Disponible'),(2,'D',8,360,160,'Disponible'),
(2,'E',1,10,210,'Disponible'),(2,'E',2,60,210,'Disponible'),(2,'E',3,110,210,'Disponible'),(2,'E',4,160,210,'Disponible'),(2,'E',5,210,210,'Disponible'),(2,'E',6,260,210,'Disponible'),(2,'E',7,310,210,'Disponible'),(2,'E',8,360,210,'Disponible'),
-- SALA 3
(3,'A',1,10,10,'Disponible'),(3,'A',2,60,10,'Disponible'),(3,'A',3,110,10,'Disponible'),(3,'A',4,160,10,'Disponible'),(3,'A',5,210,10,'Disponible'),(3,'A',6,260,10,'Disponible'),(3,'A',7,310,10,'Disponible'),(3,'A',8,360,10,'Disponible'),
(3,'B',1,10,60,'Disponible'),(3,'B',2,60,60,'Disponible'),(3,'B',3,110,60,'Disponible'),(3,'B',4,160,60,'Disponible'),(3,'B',5,210,60,'Disponible'),(3,'B',6,260,60,'Disponible'),(3,'B',7,310,60,'Disponible'),(3,'B',8,360,60,'Disponible'),
(3,'C',1,10,110,'Disponible'),(3,'C',2,60,110,'Disponible'),(3,'C',3,110,110,'Disponible'),(3,'C',4,160,110,'Disponible'),(3,'C',5,210,110,'Disponible'),(3,'C',6,260,110,'Disponible'),(3,'C',7,310,110,'Disponible'),(3,'C',8,360,110,'Disponible'),
(3,'D',1,10,160,'Disponible'),(3,'D',2,60,160,'Disponible'),(3,'D',3,110,160,'Disponible'),(3,'D',4,160,160,'Disponible'),(3,'D',5,210,160,'Disponible'),(3,'D',6,260,160,'Disponible'),(3,'D',7,310,160,'Disponible'),(3,'D',8,360,160,'Disponible'),
(3,'E',1,10,210,'Disponible'),(3,'E',2,60,210,'Disponible'),(3,'E',3,110,210,'Disponible'),(3,'E',4,160,210,'Disponible'),(3,'E',5,210,210,'Disponible'),(3,'E',6,260,210,'Disponible'),(3,'E',7,310,210,'Disponible'),(3,'E',8,360,210,'Disponible');

-- ============================================================
-- 12. TARIFAS
-- ============================================================
INSERT INTO tarifa (id_tarifa, nombre, precio, dia_aplica) VALUES
(1,  'General',         25.00, 'Todos'),
(2,  'Estudiante',      18.00, 'Todos'),
(3,  'Adulto Mayor',    15.00, 'Todos'),
(4,  'Niño (< 12)',     12.00, 'Todos'),
(5,  'Matinée',         20.00, 'Todos'),
(6,  'Miercoles Ciné',  15.00, 'Miercoles'),
(7,  'IMAX Premium',    45.00, 'Todos'),
(8,  '4DX Premium',     55.00, 'Todos'),
(9,  'Fin de Semana',   30.00, 'Sabado'),
(10, 'Fin de Semana',   30.00, 'Domingo');

-- ============================================================
-- 13. PROMOCIONES
-- ============================================================
INSERT INTO promocion (id_promocion, codigo_cupon, porcentaje_descuento, monto_descuento, fecha_inicio, fecha_fin, limite_usos) VALUES
(1,  'BIENVENIDO10', 10.00, NULL,  '2026-01-01 00:00:00', '2026-12-31 23:59:59', 500),
(2,  'ESTUDIANTE15', 15.00, NULL,  '2026-01-01 00:00:00', '2026-12-31 23:59:59', 1000),
(3,  'VERANO20',     20.00, NULL,  '2026-06-01 00:00:00', '2026-08-31 23:59:59', 300),
(4,  'CUMPLE50',     50.00, NULL,  '2026-01-01 00:00:00', '2026-12-31 23:59:59', 100),
(5,  'PRIMERAVEZ',   NULL,  5.00,  '2026-01-01 00:00:00', '2026-12-31 23:59:59', 200),
(6,  'FAMILIA4X3',   25.00, NULL,  '2026-04-01 00:00:00', '2026-06-30 23:59:59', 150),
(7,  'IMAX2024',     10.00, NULL,  '2026-01-01 00:00:00', '2026-12-31 23:59:59', 400),
(8,  'NAVIDAD25',    25.00, NULL,  '2026-12-01 00:00:00', '2026-12-31 23:59:59', 250),
(9,  'FINDE15',      15.00, NULL,  '2026-01-01 00:00:00', '2026-12-31 23:59:59', 600),
(10, 'LUNES10',      10.00, NULL,  '2026-01-01 00:00:00', '2026-12-31 23:59:59', 400);

-- ============================================================
-- 14. FUNCIONES (30 funciones)
-- ============================================================
INSERT INTO funcion (id_funcion, id_pelicula, id_sala, fecha_hora_inicio, fecha_hora_fin, idioma, formato) VALUES
(1,  1,  1, '2026-06-01 14:00:00','2026-06-01 16:46:00','Subtitulada','IMAX'),
(2,  1,  2, '2026-06-01 18:00:00','2026-06-01 20:46:00','Español',    '4DX'),
(3,  2,  1, '2026-06-02 13:00:00','2026-06-02 15:08:00','Subtitulada','IMAX'),
(4,  2,  3, '2026-06-02 17:30:00','2026-06-02 19:38:00','Español',    '2D'),
(5,  3,  7, '2026-06-03 10:00:00','2026-06-03 11:40:00','Español',    '3D'),
(6,  3,  8, '2026-06-03 14:00:00','2026-06-03 15:40:00','Español',    '2D'),
(7,  4,  4, '2026-06-01 15:00:00','2026-06-01 16:59:00','Subtitulada','IMAX'),
(8,  4,  5, '2026-06-01 20:00:00','2026-06-01 21:59:00','Español',    '3D'),
(9,  5,  10,'2026-06-02 16:00:00','2026-06-02 19:00:00','Subtitulada','IMAX'),
(10, 5,  11,'2026-06-02 20:00:00','2026-06-02 23:00:00','Español',    '3D'),
(11, 6,  8, '2026-06-03 11:00:00','2026-06-03 12:34:00','Español',    '2D'),
(12, 6,  9, '2026-06-03 15:00:00','2026-06-03 16:34:00','Español',    '4DX'),
(13, 7,  1, '2026-06-01 17:00:00','2026-06-01 19:28:00','Subtitulada','IMAX'),
(14, 7,  10,'2026-06-01 20:00:00','2026-06-01 22:28:00','Español',    'IMAX'),
(15, 8,  4, '2026-06-02 16:30:00','2026-06-02 19:10:00','Subtitulada','IMAX'),
(16, 8,  6, '2026-06-02 19:00:00','2026-06-02 21:40:00','Español',    '2D'),
(17, 10, 3, '2026-06-03 14:00:00','2026-06-03 15:49:00','Español',    '2D'),
(18, 10, 5, '2026-06-03 18:00:00','2026-06-03 19:49:00','Subtitulada','3D'),
(19, 12, 2, '2026-06-01 19:00:00','2026-06-01 21:18:00','Subtitulada','4DX'),
(20, 12, 11,'2026-06-01 15:00:00','2026-06-01 17:18:00','Español',    '3D'),
(21, 13, 7, '2026-06-02 13:00:00','2026-06-02 15:02:00','Español',    '3D'),
(22, 13, 12,'2026-06-02 17:00:00','2026-06-02 19:02:00','Subtitulada','2D'),
(23, 14, 8, '2026-06-03 16:00:00','2026-06-03 17:44:00','Español',    '2D'),
(24, 15, 3, '2026-06-03 21:00:00','2026-06-03 23:05:00','Subtitulada','2D'),
(25, 17, 1, '2026-06-01 15:00:00','2026-06-01 17:56:00','Subtitulada','IMAX'),
(26, 18, 10,'2026-06-02 14:00:00','2026-06-02 17:12:00','Subtitulada','IMAX'),
(27, 18, 4, '2026-06-02 18:00:00','2026-06-02 21:12:00','Español',    'IMAX'),
(28, 19, 7, '2026-06-03 15:00:00','2026-06-03 17:20:00','Español',    '3D'),
(29, 20, 1, '2026-06-01 19:00:00','2026-06-01 21:49:00','Subtitulada','IMAX'),
(30, 20, 2, '2026-06-01 14:00:00','2026-06-01 16:49:00','Español',    '4DX');

-- ============================================================
-- 15. FUNCION_ASIENTO
-- ============================================================
INSERT INTO funcion_asiento (id_funcion, id_asiento, estado)
SELECT 1,  id_asiento, 'Disponible' FROM asiento WHERE id_sala = 1
UNION ALL
SELECT 2,  id_asiento, 'Disponible' FROM asiento WHERE id_sala = 2
UNION ALL
SELECT 3,  id_asiento, 'Disponible' FROM asiento WHERE id_sala = 1
UNION ALL
SELECT 5,  id_asiento, 'Disponible' FROM asiento WHERE id_sala = 7
UNION ALL
SELECT 11, id_asiento, 'Disponible' FROM asiento WHERE id_sala = 8;

-- Marcar asientos vendidos/reservados en función 1 (usamos IDs reales de sala 1)
UPDATE funcion_asiento fa
JOIN asiento a ON fa.id_asiento = a.id_asiento
SET fa.estado = 'Vendido'
WHERE fa.id_funcion = 1 AND a.id_sala = 1 AND a.fila IN ('A','B') AND a.numero IN (1,2,3,4,5,6);

UPDATE funcion_asiento fa
JOIN asiento a ON fa.id_asiento = a.id_asiento
SET fa.estado = 'Reservado'
WHERE fa.id_funcion = 1 AND a.id_sala = 1 AND a.fila IN ('A','B') AND a.numero IN (7,8);

-- Marcar asientos vendidos/reservados en función 2 (sala 2)
UPDATE funcion_asiento fa
JOIN asiento a ON fa.id_asiento = a.id_asiento
SET fa.estado = 'Vendido'
WHERE fa.id_funcion = 2 AND a.id_sala = 2 AND a.fila = 'A' AND a.numero IN (1,2,3,4,5);

UPDATE funcion_asiento fa
JOIN asiento a ON fa.id_asiento = a.id_asiento
SET fa.estado = 'Reservado'
WHERE fa.id_funcion = 2 AND a.id_sala = 2 AND a.fila = 'A' AND a.numero IN (6,7);

-- ============================================================
-- 16. RESERVAS (25 reservas)
-- ============================================================
INSERT INTO reserva (id_reserva, id_usuario, id_funcion, id_promocion, fecha_reserva, fecha_expiracion, monto_subtotal, descuento_aplicado, monto_total, estado_pago, metodo_pago, transaccion_id) VALUES
(1,  3, 1,  NULL,'2026-11-01 12:00:00','2026-11-01 12:30:00',  50.00,  0.00,  50.00,'Pagado',    'Tarjeta', 'TXN-20241101-001'),
(2,  4, 1,  1,   '2026-11-01 12:15:00','2026-11-01 12:45:00',  50.00,  5.00,  45.00,'Pagado',    'Tarjeta', 'TXN-20241101-002'),
(3,  5, 2,  NULL,'2026-11-01 15:00:00','2026-11-01 15:30:00', 110.00,  0.00, 110.00,'Pagado',    'Yape',    'TXN-20241101-003'),
(4,  6, 3,  3,   '2026-11-02 10:00:00','2026-11-02 10:30:00', 128.00, 25.60, 102.40,'Pagado',    'Tarjeta', 'TXN-20241102-001'),
(5,  7, 5,  NULL,'2026-11-03 09:00:00','2026-11-03 09:30:00',  24.00,  0.00,  24.00,'Pagado',    'Plin',    'TXN-20241103-001'),
(6,  8, 6,  2,   '2026-11-03 13:00:00','2026-11-03 13:30:00',  36.00,  5.40,  30.60,'Pagado',    'Efectivo','TXN-20241103-002'),
(7,  9, 7,  NULL,'2026-11-04 14:00:00','2026-11-04 14:30:00',  45.00,  0.00,  45.00,'Pagado',    'Tarjeta', 'TXN-20241104-001'),
(8,  10,9,  7,   '2026-11-05 15:00:00','2026-11-05 15:30:00',  90.00,  9.00,  81.00,'Pagado',    'Tarjeta', 'TXN-20241105-001'),
(9,  11,10, NULL,'2026-11-05 18:00:00','2026-11-05 18:30:00',  50.00,  0.00,  50.00,'Pagado',    'Yape',    'TXN-20241105-002'),
(10, 13,11, NULL,'2026-11-06 10:30:00','2026-11-06 11:00:00',  25.00,  0.00,  25.00,'Pagado',    'Efectivo','TXN-20241106-001'),
(11, 14,12, 9,   '2026-11-06 13:30:00','2026-11-06 14:00:00',  55.00,  8.25,  46.75,'Pagado',    'Tarjeta', 'TXN-20241106-002'),
(12, 15,13, NULL,'2026-11-07 16:00:00','2026-11-07 16:30:00',  90.00,  0.00,  90.00,'Pagado',    'Tarjeta', 'TXN-20241107-001'),
(13, 16,14, 7,   '2026-11-07 18:00:00','2026-11-07 18:30:00',  45.00,  4.50,  40.50,'Pagado',    'Yape',    'TXN-20241107-002'),
(14, 17,15, NULL,'2026-11-08 15:00:00','2026-11-08 15:30:00',  45.00,  0.00,  45.00,'Pagado',    'Tarjeta', 'TXN-20241108-001'),
(15, 18,16, 1,   '2026-11-08 17:00:00','2026-11-08 17:30:00',  50.00,  5.00,  45.00,'Pagado',    'Plin',    'TXN-20241108-002'),
(16, 19,17, NULL,'2026-11-09 13:00:00','2026-11-09 13:30:00',  25.00,  0.00,  25.00,'Pagado',    'Efectivo','TXN-20241109-001'),
(17, 20,18, NULL,'2026-11-09 17:00:00','2026-11-09 17:30:00',  25.00,  0.00,  25.00,'Pagado',    'Yape',    'TXN-20241109-002'),
(18, 21,19, 4,   '2026-11-10 18:00:00','2026-11-10 18:30:00', 110.00, 55.00,  55.00,'Pagado',    'Tarjeta', 'TXN-20241110-001'),
(19, 22,21, NULL,'2026-11-11 12:00:00','2026-11-11 12:30:00',  25.00,  0.00,  25.00,'Pagado',    'Efectivo','TXN-20241111-001'),
(20, 23,22, 6,   '2026-11-11 16:00:00','2026-11-11 16:30:00', 100.00, 25.00,  75.00,'Pagado',    'Tarjeta', 'TXN-20241111-002'),
(21, 24,24, NULL,'2026-11-13 20:00:00','2026-11-13 20:30:00',  25.00,  0.00,  25.00,'Cancelado', 'Yape',    'TXN-20241113-001'),
(22, 25,25, NULL,'2026-11-14 14:00:00','2026-11-14 14:30:00',  45.00,  0.00,  45.00,'Pagado',    'Tarjeta', 'TXN-20241114-001'),
(23, 26,26, 8,   '2026-11-15 13:00:00','2026-11-15 13:30:00',  90.00, 22.50,  67.50,'Pagado',    'Tarjeta', 'TXN-20241115-001'),
(24, 27,28, NULL,'2026-11-16 14:00:00','2026-11-16 14:30:00',  50.00,  0.00,  50.00,'Pendiente', 'Tarjeta', 'TXN-20241116-001'),
(25, 28,30, 2,   '2026-11-17 13:00:00','2026-11-17 13:30:00', 110.00, 16.50,  93.50,'Pagado',    'Plin',    'TXN-20241117-001');

-- ============================================================
-- 17. BOLETOS
--     Solo se insertan boletos para reservas pagadas.
--     Los id_asiento referenciados deben existir en funcion_asiento.
--     Usamos asientos de sala 1 (funcion 1 y 3) y sala 2 (funcion 2).
-- ============================================================
INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    1, 1, 1, a.id_asiento, 1,
    'QR-FLM-20241101-0001', 25.00, 'Usado'
FROM asiento a WHERE a.id_sala = 1 AND a.fila = 'A' AND a.numero = 1;

INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    2, 1, 1, a.id_asiento, 1,
    'QR-FLM-20241101-0002', 25.00, 'Usado'
FROM asiento a WHERE a.id_sala = 1 AND a.fila = 'A' AND a.numero = 2;

INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    3, 2, 1, a.id_asiento, 1,
    'QR-FLM-20241101-0003', 22.50, 'Usado'
FROM asiento a WHERE a.id_sala = 1 AND a.fila = 'A' AND a.numero = 3;

INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    4, 2, 1, a.id_asiento, 1,
    'QR-FLM-20241101-0004', 22.50, 'Usado'
FROM asiento a WHERE a.id_sala = 1 AND a.fila = 'A' AND a.numero = 4;

INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    5, 3, 2, a.id_asiento, 8,
    'QR-FLM-20241101-0005', 55.00, 'Vigente'
FROM asiento a WHERE a.id_sala = 2 AND a.fila = 'A' AND a.numero = 1;

INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    6, 3, 2, a.id_asiento, 8,
    'QR-FLM-20241101-0006', 55.00, 'Vigente'
FROM asiento a WHERE a.id_sala = 2 AND a.fila = 'A' AND a.numero = 2;

INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    7, 4, 3, a.id_asiento, 1,
    'QR-FLM-20241102-0001', 25.60, 'Usado'
FROM asiento a WHERE a.id_sala = 1 AND a.fila = 'A' AND a.numero = 5;

INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    8, 4, 3, a.id_asiento, 1,
    'QR-FLM-20241102-0002', 25.60, 'Usado'
FROM asiento a WHERE a.id_sala = 1 AND a.fila = 'A' AND a.numero = 6;

INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    9, 4, 3, a.id_asiento, 1,
    'QR-FLM-20241102-0003', 25.60, 'Usado'
FROM asiento a WHERE a.id_sala = 1 AND a.fila = 'B' AND a.numero = 1;

INSERT INTO boleto (id_boleto, id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso)
SELECT
    10, 4, 3, a.id_asiento, 1,
    'QR-FLM-20241102-0004', 25.60, 'Usado'
FROM asiento a WHERE a.id_sala = 1 AND a.fila = 'B' AND a.numero = 2;

-- ============================================================
-- 18. CATEGORÍAS DE SNACK
-- ============================================================
INSERT INTO categoria_snack (id_categoria, nombre, orden_visual, estado) VALUES
(1, 'Bebidas',         1, TRUE),
(2, 'Combos',          2, TRUE),
(3, 'Palomitas',       3, TRUE),
(4, 'Dulces y Snacks', 4, TRUE),
(5, 'Comida Rapida',   5, TRUE),
(6, 'Sin Azucar',      6, TRUE);

-- ============================================================
-- 19. PRODUCTOS SNACK (24 productos)
-- ============================================================
INSERT INTO producto_snack (id_producto, id_categoria, nombre, descripcion, precio_actual, url_imagen, is_activo) VALUES
(1,  3, 'Palomitas Pequeñas',  'Palomitas de maíz mantequilla 60gr',               8.00, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=300', TRUE),
(2,  3, 'Palomitas Medianas',  'Palomitas de maíz mantequilla 120gr',             12.00, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=300', TRUE),
(3,  3, 'Palomitas Grandes',   'Palomitas de maíz mantequilla 200gr',             16.00, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=300', TRUE),
(4,  3, 'Palomitas Caramelo',  'Palomitas bañadas en caramelo 150gr',             14.00, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=300', TRUE),
(5,  1, 'Gaseosa Pequeña',     'Gaseosa 300ml (Coca-Cola, Inca Kola, Sprite)',     7.00, 'https://images.unsplash.com/photo-1554866585-cd94860890b7?w=300', TRUE),
(6,  1, 'Gaseosa Mediana',     'Gaseosa 500ml',                                    9.00, 'https://images.unsplash.com/photo-1554866585-cd94860890b7?w=300', TRUE),
(7,  1, 'Gaseosa Grande',      'Gaseosa 700ml',                                   11.00, 'https://images.unsplash.com/photo-1554866585-cd94860890b7?w=300', TRUE),
(8,  1, 'Agua Mineral',        'Agua mineral 600ml',                               4.00, 'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300', TRUE),
(9,  1, 'Jugo de Naranja',     'Jugo natural de naranja 400ml',                    9.00, 'https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=300', TRUE),
(10, 1, 'Café Americano',      'Café americano caliente 12oz',                     8.00, 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=300', TRUE),
(11, 2, 'Combo Dúo',           'Palomitas medianas + 2 gaseosas medianas',        28.00, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=300', TRUE),
(12, 2, 'Combo Familiar',      'Palomitas grandes + 4 gaseosas medianas',         48.00, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=300', TRUE),
(13, 2, 'Combo Clásico',       'Palomitas pequeñas + 1 gaseosa mediana',          17.00, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=300', TRUE),
(14, 2, 'Combo Premium IMAX',  'Palomitas grandes + 2 gaseosas grandes + dulce',  45.00, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=300', TRUE),
(15, 4, 'Nachos con Queso',    'Nachos crujientes con salsa de queso 150gr',      12.00, 'https://images.unsplash.com/photo-1513456852971-30c0b8199d4d?w=300', TRUE),
(16, 4, 'M&Ms',                'M&Ms chocolate 100gr',                             7.00, 'https://images.unsplash.com/photo-1548907040-4baa42d10919?w=300', TRUE),
(17, 4, 'Chocolates Surtidos', 'Caja de chocolates surtidos 200gr',               15.00, 'https://images.unsplash.com/photo-1548907040-4baa42d10919?w=300', TRUE),
(18, 4, 'Gomitas Haribo',      'Gomitas de fruta Haribo 100gr',                    6.00, 'https://images.unsplash.com/photo-1602145862039-a8dcda1f4ee9?w=300', TRUE),
(19, 5, 'Hot Dog Clásico',     'Hot dog con pan, mostaza y ketchup',              12.00, 'https://images.unsplash.com/photo-1583835746434-cf1534674b41?w=300', TRUE),
(20, 5, 'Pizza Personal',      'Pizza personal de pepperoni (2 porciones)',        18.00, 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=300', TRUE),
(21, 5, 'Nuggets de Pollo',    '6 nuggets de pollo con salsa',                    14.00, 'https://images.unsplash.com/photo-1562967914-608f82629710?w=300', TRUE),
(22, 6, 'Agua con Gas',        'Agua con gas sin azúcar 500ml',                    5.00, 'https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=300', TRUE),
(23, 6, 'Palomitas Sin Sal',   'Palomitas sin sal ni mantequilla 120gr',          10.00, 'https://images.unsplash.com/photo-1585647347483-22b66260dfff?w=300', TRUE),
(24, 6, 'Barrita de Granola',  'Barrita de granola con frutos secos 45gr',         6.00, 'https://images.unsplash.com/photo-1623428187969-5da2dcea5ebf?w=300', TRUE);

-- ============================================================
-- 20. RESERVAS SNACK
-- ============================================================
INSERT INTO reserva_snack (id_reserva, id_producto, cantidad, precio_unitario) VALUES
(1,  2,  1, 12.00),
(1,  6,  2,  9.00),
(2,  11, 1, 28.00),
(3,  12, 1, 48.00),
(3,  10, 2,  8.00),
(4,  13, 4, 17.00),
(5,  1,  1,  8.00),
(5,  5,  1,  7.00),
(6,  3,  1, 16.00),
(6,  7,  2, 11.00),
(7,  14, 1, 45.00),
(8,  12, 1, 48.00),
(8,  9,  2,  9.00),
(9,  2,  2, 12.00),
(9,  6,  2,  9.00),
(10, 1,  1,  8.00),
(10, 5,  1,  7.00),
(11, 11, 2, 28.00),
(12, 14, 2, 45.00),
(13, 3,  1, 16.00),
(13, 7,  2, 11.00),
(14, 13, 1, 17.00),
(14, 6,  1,  9.00),
(15, 11, 1, 28.00),
(16, 2,  1, 12.00),
(17, 15, 2, 12.00),
(18, 12, 1, 48.00),
(19, 1,  1,  8.00),
(19, 5,  2,  7.00),
(20, 11, 3, 28.00),
(22, 14, 2, 45.00),
(23, 12, 1, 48.00),
(25, 3,  2, 16.00),
(25, 7,  3, 11.00);

-- ============================================================
-- 21. RESEÑAS (40 reseñas)
-- ============================================================
INSERT INTO resena (id_usuario, id_pelicula, calificacion_estrellas, comentario, estado_moderacion, fecha_publicacion) VALUES
(3,  1,  5.0, 'Absolutamente épica. Denis Villeneuve lo volvió a hacer. Las escenas del desierto son impresionantes.',          'Aprobado','2026-11-02 10:00:00'),
(4,  1,  4.5, 'Mejor que la primera parte. Zendaya roba cada escena que tiene.',                                                'Aprobado','2026-11-02 14:30:00'),
(5,  1,  4.0, 'Gran película pero algo larga. La música de Hans Zimmer es brutal.',                                             'Aprobado','2026-11-03 09:00:00'),
(6,  2,  5.0, 'La mejor película del MCU en años! Ryan Reynolds y Hugh Jackman tienen una química increíble.',                  'Aprobado','2026-11-03 12:00:00'),
(7,  2,  4.5, 'Muy divertida y llena de fan service de calidad. Me reí todo el tiempo.',                                        'Aprobado','2026-11-03 16:00:00'),
(8,  2,  3.5, 'Entretenida pero demasiadas referencias al multiverso. Aun así valió la pena.',                                  'Aprobado','2026-11-04 10:00:00'),
(9,  3,  5.0, 'Ansiedad es un personaje fantástico! Pixar volvió a emocionarme profundamente.',                                 'Aprobado','2026-11-04 14:00:00'),
(10, 3,  4.5, 'Lloré sin parar. Muy identificable para cualquier persona que haya sido adolescente.',                           'Aprobado','2026-11-05 11:00:00'),
(11, 3,  4.0, 'Muy buena secuela aunque la primera es superior. Los niños la amaron.',                                          'Aprobado','2026-11-05 15:00:00'),
(13, 4,  4.5, 'Aterradora y hermosa a la vez. Los efectos especiales son de otro nivel.',                                       'Aprobado','2026-11-05 18:00:00'),
(14, 4,  4.0, 'Si eres fan del Alien original la vas a amar. Muy buen regreso a las raíces.',                                   'Aprobado','2026-11-06 09:00:00'),
(15, 5,  5.0, 'Una obra maestra cinematográfica. Cillian Murphy merece el Oscar sin duda.',                                     'Aprobado','2026-11-06 12:00:00'),
(16, 5,  5.0, 'Nolan en su máximo esplendor. Cada plano es una fotografía perfecta.',                                           'Aprobado','2026-11-06 16:00:00'),
(17, 5,  4.5, 'Intensa y reflexiva. La escena del juicio es de las mejores que he visto.',                                      'Aprobado','2026-11-07 10:00:00'),
(18, 6,  4.0, 'Divertida para toda la familia. Po sigue siendo adorable.',                                                      'Aprobado','2026-11-07 14:00:00'),
(19, 6,  3.5, 'Entretenida pero no al nivel de las primeras dos. Aun así los niños disfrutaron.',                               'Aprobado','2026-11-08 10:00:00'),
(20, 7,  4.5, 'Paul Mescal es una revelación. El Coliseo se ve espectacular en IMAX.',                                          'Aprobado','2026-11-08 14:00:00'),
(21, 7,  4.0, 'Digna secuela aunque Crowe era insuperable. La acción es brutal.',                                               'Aprobado','2026-11-08 18:00:00'),
(22, 8,  5.0, 'Cynthia Erivo y Ariana Grande son perfectas. Lloré de emoción durante toda la película.',                       'Aprobado','2026-11-09 11:00:00'),
(23, 8,  5.0, 'Asombrosa! Las canciones, el vestuario, la actuación. Todo de primer nivel.',                                    'Aprobado','2026-11-09 15:00:00'),
(24, 10, 3.5, 'Decepcionante para cerrar la trilogía. Tom Hardy lo da todo pero el guion falla.',                               'Aprobado','2026-11-10 10:00:00'),
(25, 10, 3.0, 'Esperaba más. La historia se siente apresurada y sin profundidad.',                                              'Aprobado','2026-11-10 14:00:00'),
(26, 12, 4.0, 'Visualmente impresionante. Lady Gaga como Harley es genial aunque la trama es divisiva.',                       'Aprobado','2026-11-11 10:00:00'),
(27, 12, 3.0, 'No era lo que esperaba. Muy diferente al Joker original.',                                                       'Aprobado','2026-11-11 15:00:00'),
(28, 13, 4.0, 'Adrenalina pura. Las escenas de los tornados son increíbles en sala grande.',                                    'Aprobado','2026-11-12 10:00:00'),
(3,  14, 4.5, 'Tim Burton regresó a sus raíces. Michael Keaton insuperable como Beetlejuice.',                                  'Aprobado','2026-11-12 14:00:00'),
(4,  15, 4.5, 'No apta para todos pero artísticamente es única. Art el Payaso es icónico.',                                     'Aprobado','2026-11-13 22:00:00'),
(5,  15, 5.0, 'La mejor película de terror de los últimos años. Brutalmente brillante.',                                        'Aprobado','2026-11-14 10:00:00'),
(6,  17, 5.0, 'Robert Pattinson redefine a Batman. Oscura, atmosférica y perfecta.',                                            'Aprobado','2026-11-14 14:00:00'),
(7,  17, 4.5, 'Impresionante. La lluvia de Gotham se siente real. Riddler da miedo de verdad.',                                 'Aprobado','2026-11-15 10:00:00'),
(8,  18, 4.5, 'Visualmente la película más hermosa que he visto. Pandora te atrapa.',                                           'Aprobado','2026-11-15 14:00:00'),
(9,  18, 4.0, 'Larga pero vale cada minuto. Cameron es un genio visual sin discusión.',                                         'Aprobado','2026-11-16 10:00:00'),
(10, 19, 5.0, 'La mejor película animada de la historia! El arte y la historia son perfectos.',                                 'Aprobado','2026-11-16 14:00:00'),
(11, 19, 5.0, 'Miles Morales es el mejor Spider-Man. La animación rompe todos los esquemas.',                                   'Aprobado','2026-11-17 10:00:00'),
(13, 19, 4.5, 'Innovadora en todo sentido. Sony Animation lo logró de nuevo.',                                                  'Aprobado','2026-11-17 14:00:00'),
(14, 20, 4.5, 'John Wick 4 es acción de alta costura. La escena del Arco de Triunfo es histórica.',                            'Aprobado','2026-11-18 10:00:00'),
(15, 20, 5.0, 'La mejor entrega de la saga. Keanu Reeves en estado puro.',                                                      'Aprobado','2026-11-18 14:00:00'),
(16, 2,  5.0, 'El cameo sorpresa me hizo llorar de emoción. Marvel sabe cómo hacerlo.',                                         'Aprobado','2026-11-18 18:00:00'),
(17, 5,  4.0, 'Necesitas verla dos veces para entender todo. Magistral pero exigente.',                                         'Aprobado','2026-11-19 10:00:00'),
(18, 1,  4.5, 'La historia de amor entre Paul y Chani es lo más bello del año.',                                                'Aprobado','2026-11-19 14:00:00');

-- ============================================================
-- 22. FAVORITOS
-- ============================================================
INSERT INTO favorito (id_usuario, id_pelicula, fecha_agregado) VALUES
(3,  1,  '2026-11-02 11:00:00'),
(3,  5,  '2026-11-06 13:00:00'),
(3,  17, '2026-11-14 15:00:00'),
(4,  2,  '2026-11-03 13:00:00'),
(4,  8,  '2026-11-09 12:00:00'),
(5,  1,  '2026-11-03 10:00:00'),
(5,  19, '2026-11-17 11:00:00'),
(6,  2,  '2026-11-03 13:00:00'),
(6,  3,  '2026-11-04 15:00:00'),
(7,  3,  '2026-11-04 16:00:00'),
(7,  6,  '2026-11-07 15:00:00'),
(8,  4,  '2026-11-05 19:00:00'),
(8,  18, '2026-11-15 15:00:00'),
(9,  7,  '2026-11-08 15:00:00'),
(9,  20, '2026-11-18 11:00:00'),
(10, 5,  '2026-11-06 13:00:00'),
(10, 19, '2026-11-16 15:00:00'),
(11, 8,  '2026-11-09 12:00:00'),
(11, 9,  '2026-11-09 13:00:00'),
(13, 4,  '2026-11-05 19:00:00'),
(14, 5,  '2026-11-06 13:00:00'),
(15, 5,  '2026-11-06 14:00:00'),
(16, 7,  '2026-11-08 15:00:00'),
(17, 8,  '2026-11-09 12:00:00'),
(18, 8,  '2026-11-09 13:00:00'),
(19, 13, '2026-11-12 11:00:00'),
(20, 14, '2026-11-12 15:00:00'),
(22, 12, '2026-11-11 11:00:00'),
(23, 17, '2026-11-14 15:00:00'),
(25, 17, '2026-11-14 16:00:00'),
(26, 20, '2026-11-18 11:00:00'),
(27, 20, '2026-11-18 12:00:00'),
(28, 19, '2026-11-17 11:00:00');

-- ============================================================
-- VERIFICACIÓN
-- ============================================================
SELECT 'usuarios'         AS tabla, COUNT(*) AS total FROM usuario
UNION ALL SELECT 'peliculas',     COUNT(*) FROM pelicula
UNION ALL SELECT 'funciones',     COUNT(*) FROM funcion
UNION ALL SELECT 'reservas',      COUNT(*) FROM reserva
UNION ALL SELECT 'boletos',       COUNT(*) FROM boleto
UNION ALL SELECT 'resenas',       COUNT(*) FROM resena
UNION ALL SELECT 'favoritos',     COUNT(*) FROM favorito
UNION ALL SELECT 'snacks',        COUNT(*) FROM producto_snack;
USE filmate_db;

USE filmate_db;

-- TABLAS PARA DEVOLUCIONES Y REEMBOLSOS

CREATE TABLE motivo_devolucion (
    id_motivo INT AUTO_INCREMENT PRIMARY KEY,
    descripcion VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE solicitud_reembolso (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    id_reserva INT NOT NULL,
    id_motivo INT NOT NULL,
    id_administrador INT NULL, -- Admin que aprueba/rechaza
    fecha_solicitud DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monto_reembolsado DECIMAL(10,2) NOT NULL,
    tipo_reembolso ENUM('Reembolso total', 'Reembolso parcial', 'Sin reembolso') NOT NULL,
    estado_solicitud ENUM('Pendiente', 'Aprobada', 'Rechazada') DEFAULT 'Pendiente',
    detalle_motivo TEXT NULL, -- Detalle del cliente
    comentario_resolucion TEXT NULL, -- ❌ Razón del rechazo/resolución del Admin
    fecha_resolucion DATETIME NULL,
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva),
    FOREIGN KEY (id_motivo) REFERENCES motivo_devolucion(id_motivo),
    FOREIGN KEY (id_administrador) REFERENCES usuario(id_usuario)
);

CREATE INDEX idx_reembolso_estado ON solicitud_reembolso(estado_solicitud, fecha_solicitud);
USE filmate_db;

-- 1. MOTIVOS DE DEVOLUCIÓN
INSERT INTO motivo_devolucion (id_motivo, descripcion) VALUES
(1, 'Cancelación de función'),
(2, 'Error de cobro'),
(3, 'Inconveniente del cliente'),
(4, 'Asiento defectuoso'),
(5, 'Fuera de política');

-- 2. RESERVAS REALES 

-- TXN-2049 (Andrés Quispe - id_usuario: 3) -> Pendiente
INSERT INTO reserva (id_reserva, id_usuario, id_funcion, fecha_reserva, fecha_expiracion, monto_subtotal, monto_total, estado_pago, transaccion_id)
VALUES (2049, 3, 1, '2026-05-08 14:00:00', '2026-05-08 14:30:00', 55.00, 55.00, 'Pendiente', 'TXN-2049');

-- TXN-2041 (Lucía Paredes - id_usuario: 4) -> Pendiente
INSERT INTO reserva (id_reserva, id_usuario, id_funcion, fecha_reserva, fecha_expiracion, monto_subtotal, monto_total, estado_pago, transaccion_id)
VALUES (2041, 4, 1, '2026-05-07 19:00:00', '2026-05-07 19:30:00', 42.00, 42.00, 'Pendiente', 'TXN-2041');

-- TXN-2038 (Miguel Ramos - id_usuario: 5) -> Reembolsado parcial (S/. 32.00)
INSERT INTO reserva (id_reserva, id_usuario, id_funcion, fecha_reserva, fecha_expiracion, monto_subtotal, monto_total, estado_pago, transaccion_id)
VALUES (2038, 5, 2, '2026-05-06 11:15:00', '2026-05-06 11:45:00', 32.00, 32.00, 'Reembolsado', 'TXN-2038');

-- TXN-2035 (Sofía Gutierrez - id_usuario: 6) -> Reembolsado parcial (S/. 18.00)
INSERT INTO reserva (id_reserva, id_usuario, id_funcion, fecha_reserva, fecha_expiracion, monto_subtotal, monto_total, estado_pago, transaccion_id)
VALUES (2035, 6, 2, '2026-05-05 16:20:00', '2026-05-05 16:50:00', 18.00, 18.00, 'Reembolsado', 'TXN-2035');

-- TXN-2030 (Diego Llanos - id_usuario: 7) -> Rechazado (S/. 0.00 / Sin reembolso)
INSERT INTO reserva (id_reserva, id_usuario, id_funcion, fecha_reserva, fecha_expiracion, monto_subtotal, monto_total, estado_pago, transaccion_id)
VALUES (2030, 7, 3, '2026-05-04 10:00:00', '2026-05-04 10:30:00', 28.00, 28.00, 'Pagado', 'TXN-2030');

-- TXN-2028 (Camila Flores - id_usuario: 8) -> Reembolsados (5 devoluciones de S/. 26.00 cada una)
INSERT INTO reserva (id_reserva, id_usuario, id_funcion, fecha_reserva, fecha_expiracion, monto_subtotal, monto_total, estado_pago, transaccion_id)
VALUES (2028, 8, 4, '2026-05-03 15:45:00', '2026-05-03 16:15:00', 130.00, 130.00, 'Reembolsado', 'TXN-2028');


-- 3. INSERCIÓN DE LAS SOLICITUDES

-- 1. Andrés Quispe (Pendiente en UI)
INSERT INTO solicitud_reembolso (id_reserva, id_motivo, id_administrador, fecha_solicitud, monto_reembolsado, tipo_reembolso, estado_solicitud, detalle_motivo)
VALUES (2049, 1, NULL, '2026-05-09 10:30:00', 55.00, 'Reembolso total', 'Pendiente', 'Función suspendida por falla técnica');

-- 2. Lucía Paredes (Pendiente en UI)
INSERT INTO solicitud_reembolso (id_reserva, id_motivo, id_administrador, fecha_solicitud, monto_reembolsado, tipo_reembolso, estado_solicitud, detalle_motivo)
VALUES (2041, 2, NULL, '2026-05-08 14:15:00', 42.00, 'Reembolso total', 'Pendiente', 'Cobro duplicado por falla en pasarela');

-- 3. Miguel Ramos (Aprobada - S/. 32.00)
INSERT INTO solicitud_reembolso (id_reserva, id_motivo, id_administrador, fecha_solicitud, monto_reembolsado, tipo_reembolso, estado_solicitud, detalle_motivo, fecha_resolucion)
VALUES (2038, 3, 1, '2026-05-07 09:10:00', 32.00, 'Reembolso parcial', 'Aprobada', 'No pudo asistir por emergencia', '2026-05-07 12:00:00');

-- 4. Sofía Gutierrez (Aprobada - S/. 18.00)
INSERT INTO solicitud_reembolso (id_reserva, id_motivo, id_administrador, fecha_solicitud, monto_reembolsado, tipo_reembolso, estado_solicitud, detalle_motivo, fecha_resolucion)
VALUES (2035, 4, 1, '2026-05-06 18:00:00', 18.00, 'Reembolso parcial', 'Aprobada', 'Asiento roto durante la función', '2026-05-07 08:30:00');

-- 5. Diego Llanos (❌ Rechazada - Incluye comentario_resolucion)
INSERT INTO solicitud_reembolso (id_reserva, id_motivo, id_administrador, fecha_solicitud, monto_reembolsado, tipo_reembolso, estado_solicitud, detalle_motivo, comentario_resolucion, fecha_resolucion)
VALUES (2030, 5, 1, '2026-05-05 11:22:00', 0.00, 'Sin reembolso', 'Rechazada', 'Solicitó reembolso tras la función', 'Solicitud fuera del plazo permitido de 48 horas.', '2026-05-05 14:00:00');

-- 6 al 10. Camila Flores (5 solicitudes aprobadas de S/. 26.00 cada una = S/. 130.00)
INSERT INTO solicitud_reembolso (id_reserva, id_motivo, id_administrador, fecha_solicitud, monto_reembolsado, tipo_reembolso, estado_solicitud, detalle_motivo, fecha_resolucion) VALUES
(2028, 1, 1, '2026-05-04 08:00:00', 26.00, 'Reembolso total', 'Aprobada', 'Película retirada de cartelera', '2026-05-04 10:00:00'),
(2028, 1, 1, '2026-05-04 08:00:00', 26.00, 'Reembolso total', 'Aprobada', 'Película retirada de cartelera', '2026-05-04 10:00:00'),
(2028, 1, 1, '2026-05-04 08:00:00', 26.00, 'Reembolso total', 'Aprobada', 'Película retirada de cartelera', '2026-05-04 10:00:00'),
(2028, 1, 1, '2026-05-04 08:00:00', 26.00, 'Reembolso total', 'Aprobada', 'Película retirada de cartelera', '2026-05-04 10:00:00'),
(2028, 1, 1, '2026-05-04 08:00:00', 26.00, 'Reembolso total', 'Aprobada', 'Película retirada de cartelera', '2026-05-04 10:00:00');


-- 4. CONTROL EFECTIVO DE CONTADORES DE LAS CARDS 

-- Agregar 6 pendientes extras para llegar a los 8 de la maqueta (Monto 0 para no alterar nada)
INSERT INTO solicitud_reembolso (id_reserva, id_motivo, monto_reembolsado, tipo_reembolso, estado_solicitud)
SELECT 2041, 3, 0.00, 'Reembolso parcial', 'Pendiente' FROM usuario LIMIT 6;

-- Agregar 15 aprobadas extras con monto 0.00 para llegar a las 22 de la maqueta sin romper la suma
INSERT INTO solicitud_reembolso (id_reserva, id_motivo, id_administrador, monto_reembolsado, tipo_reembolso, estado_solicitud)
SELECT 2038, 3, 1, 0.00, 'Reembolso parcial', 'Aprobada' FROM usuario LIMIT 15;

-- Agregar 3 rechazadas extras con su respectivo motivo de rechazo para cerrar las 34 totales
INSERT INTO solicitud_reembolso (id_reserva, id_motivo, id_administrador, monto_reembolsado, tipo_reembolso, estado_solicitud, comentario_resolucion)
SELECT 2030, 5, 1, 0.00, 'Sin reembolso', 'Rechazada', 'No cumple con las políticas institucionales de la empresa.' FROM usuario LIMIT 3;

CREATE TABLE director (
    id_director INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE pelicula_director (
    id_pelicula INT NOT NULL,
    id_director INT NOT NULL,
    PRIMARY KEY (id_pelicula, id_director),
    FOREIGN KEY (id_pelicula) REFERENCES pelicula(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_director) REFERENCES director(id_director) ON DELETE CASCADE
);
USE filmate_db;

-- ============================================================
-- DIRECTORES
-- ============================================================
INSERT INTO director (id_director, nombre) VALUES
(1,  'Denis Villeneuve'),
(2,  'Shawn Levy'),
(3,  'Kelsey Mann'),
(4,  'Fede Álvarez'),
(5,  'Christopher Nolan'),
(6,  'Mike Mitchell'),
(7,  'Ridley Scott'),
(8,  'Jon M. Chu'),
(9,  'David G. Derrick Jr.'),
(10, 'Kelly Marcel'),
(11, 'Kenji Kamiyama'),
(12, 'Todd Phillips'),
(13, 'Lee Isaac Chung'),
(14, 'Tim Burton'),
(15, 'Damien Leone'),
(16, 'James Wan'),
(17, 'Matt Reeves'),
(18, 'James Cameron'),
(19, 'Joaquim Dos Santos'),
(20, 'Kemp Powers'),
(21, 'Justin K. Thompson'),
(22, 'Chad Stahelski');

-- ============================================================
-- RELACIÓN PELÍCULA–DIRECTOR
-- ============================================================
INSERT INTO pelicula_director (id_pelicula, id_director) VALUES
(1,  1),  -- Dune: Parte Dos -> Denis Villeneuve
(2,  2),  -- Deadpool & Wolverine -> Shawn Levy
(3,  3),  -- Inside Out 2 -> Kelsey Mann
(4,  4),  -- Alien: Romulus -> Fede Álvarez
(5,  5),  -- Oppenheimer -> Christopher Nolan
(6,  6),  -- Kung Fu Panda 4 -> Mike Mitchell
(7,  7),  -- Gladiador II -> Ridley Scott
(8,  8),  -- Wicked -> Jon M. Chu
(9,  9),  -- Moana 2 -> David G. Derrick Jr.
(10, 10), -- Venom: El Último Baile -> Kelly Marcel
(11, 11), -- El Señor de los Anillos: La Guerra de los Rohirrim -> Kenji Kamiyama
(12, 12), -- Joker: Folie à Deux -> Todd Phillips
(13, 13), -- Twisters -> Lee Isaac Chung
(14, 14), -- Beetlejuice Beetlejuice -> Tim Burton
(15, 15), -- Terrifier 3 -> Damien Leone
(16, 16), -- Aquaman y el Reino Perdido -> James Wan
(17, 17), -- The Batman -> Matt Reeves
(18, 18), -- Avatar: El Camino del Agua -> James Cameron
-- Spider-Man: Cruzando el Multiverso tiene 3 directores:
(19, 19), 
(19, 20), 
(19, 21), 
(20, 22); -- John Wick 4 -> Chad Stahelski
