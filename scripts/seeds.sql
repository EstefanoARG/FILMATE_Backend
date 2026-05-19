INSERT INTO rol (nombre) VALUES 
('Admin'), 
('Cliente');

INSERT INTO usuario (id_rol, nombres, apellidos, correo, password_hash, estado) VALUES
(1, 'Valeria', 'Campos', 'admin@filmate.com', '$2y$10$abcdefghijklmnopqrstuv', 'Activo'),
(2, 'Jorge', 'Salinas', 'jsalinas88@gmail.com', '$2y$10$zyxwvutsrqponmlkjihgfe', 'Activo'),
(2, 'Camila', 'Reyes', 'camila.reyes@hotmail.com', '$2y$10$1234567890abcdefghijkl', 'Activo');

INSERT INTO pelicula (titulo, sinopsis, duracion_minutos, clasificacion_edad, url_poster, url_trailer, categoria_cartelera) VALUES
('Dune: Parte Dos', 'Paul Atreides se une a Chani y a los Fremen mientras busca venganza contra los conspiradores que destruyeron a su familia.', 166, '+14', 'https://img.filmate.com/posters/dune2.jpg', 'https://youtube.com/dune2', 'Cartelera'),
('Intensa-Mente 2', 'Alegría, Tristeza, Furia, Temor y Desagrado reciben a nuevas emociones en el cuartel general.', 96, 'APT', 'https://img.filmate.com/posters/insideout2.jpg', 'https://youtube.com/io2', 'Estreno'),
('Deadpool & Wolverine', 'Wolverine se recupera de sus heridas cuando se cruza con Deadpool, juntos formarán un equipo inesperado.', 127, '+18', 'https://img.filmate.com/posters/dp3.jpg', 'https://youtube.com/dp3', 'Preventa');

INSERT INTO genero (nombre) VALUES 
('Ciencia Ficción'), ('Animación'), ('Acción'), ('Comedia'), ('Fantasía');

INSERT INTO pelicula_genero (id_pelicula, id_genero) VALUES 
(1, 1), (1, 3),
(2, 2), (2, 4),
(3, 3), (3, 4);

INSERT INTO actor (nombre) VALUES 
('Timothée Chalamet'), ('Zendaya'), ('Amy Poehler'), ('Ryan Reynolds'), ('Hugh Jackman');

INSERT INTO pelicula_actor (id_pelicula, id_actor, personaje) VALUES 
(1, 1, 'Paul Atreides'),
(1, 2, 'Chani'),
(2, 3, 'Alegría (Voz)'),
(3, 4, 'Wade Wilson / Deadpool'),
(3, 5, 'Logan / Wolverine');

INSERT INTO banner_home (id_pelicula, imagen_url, orden, is_activo) VALUES
(2, 'https://img.filmate.com/banners/insideout2_wide.jpg', 1, TRUE),
(3, 'https://img.filmate.com/banners/deadpool_wide.jpg', 2, TRUE),
(1, 'https://img.filmate.com/banners/dune_wide.jpg', 3, TRUE);

INSERT INTO resena (id_usuario, id_pelicula, calificacion_estrellas, comentario, estado_moderacion) VALUES
(2, 1, 5.0, 'Visualmente espectacular. Una obra maestra de la ciencia ficción moderna, superó a la primera parte.', 'Aprobado'),
(3, 1, 4.5, 'Me encantó la banda sonora, aunque se siente un poco larga hacia el final.', 'Aprobado');

INSERT INTO favorito (id_usuario, id_pelicula) VALUES 
(2, 1), (2, 3),
(3, 2);

INSERT INTO cine (nombre, direccion, ciudad, estado) VALUES 
('Filmate Norte', 'Mall Aventura 550', 'Trujillo', TRUE);

INSERT INTO sala (id_cine, nombre, formato_sala, capacidad_total) VALUES 
(1, 'Sala 1 - MACRO XE', '2D', 6),
(1, 'Sala 2 - VIP', '2D', 4);

INSERT INTO asiento (id_sala, fila, numero, coord_x, coord_y, estado_fisico) VALUES
(1, 'A', 1, 0, 0, 'Disponible'), (1, 'A', 2, 1, 0, 'Disponible'), (1, 'A', 3, 2, 0, 'Disponible'),
(1, 'B', 1, 0, 1, 'Disponible'), (1, 'B', 2, 1, 1, 'Disponible'), (1, 'B', 3, 2, 1, 'Disponible');

INSERT INTO asiento (id_sala, fila, numero, coord_x, coord_y, estado_fisico) VALUES
(2, 'A', 1, 0, 0, 'Disponible'), (2, 'A', 2, 1, 0, 'Disponible'),
(2, 'B', 1, 0, 1, 'Disponible'), (2, 'B', 2, 1, 1, 'Disponible');

INSERT INTO tarifa (nombre, precio, dia_aplica) VALUES 
('General', 22.50, 'Todos'), 
('Niños y Tercera Edad', 16.00, 'Todos'), 
('Martes Loco', 12.00, 'Martes');

INSERT INTO promocion (codigo_cupon, porcentaje_descuento, monto_descuento, fecha_inicio, fecha_fin, limite_usos) VALUES
('FILMATE2026', 10.00, NULL, '2026-05-01 00:00:00', '2026-12-31 23:59:59', 500);

INSERT INTO funcion (id_pelicula, id_sala, fecha_hora_inicio, fecha_hora_fin, idioma, formato) VALUES
(1, 1, '2026-05-25 19:00:00', '2026-05-25 22:00:00', 'Subtitulada', 'MACRO XE'),
(2, 2, '2026-05-25 16:00:00', '2026-05-25 18:00:00', 'Doblada', 'VIP');

INSERT INTO funcion_asiento (id_funcion, id_asiento, estado) VALUES
(1, 1, 'Vendido'), (1, 2, 'Vendido'), (1, 3, 'Disponible'),
(1, 4, 'Disponible'), (1, 5, 'Disponible'), (1, 6, 'Disponible');

INSERT INTO reserva (id_usuario, id_funcion, id_promocion, fecha_expiracion, monto_subtotal, descuento_aplicado, monto_total, estado_pago, metodo_pago, transaccion_id) VALUES
(2, 1, NULL, '2026-05-25 18:50:00', 45.00, 0.00, 45.00, 'Pagado', 'Tarjeta de Crédito', 'TXN-987654ABC');

INSERT INTO boleto (id_reserva, id_funcion, id_asiento, id_tarifa, codigo_qr, precio_pagado, estado_ingreso) VALUES
(1, 1, 1, 1, 'QR_TK_1001_FUNC1_AS1', 22.50, 'Vigente'),
(1, 1, 2, 1, 'QR_TK_1002_FUNC1_AS2', 22.50, 'Vigente');

INSERT INTO categoria_snack (nombre, orden_visual, estado) VALUES 
('Combos', 1, TRUE), 
('Cancha / Popcorn', 2, TRUE), 
('Bebidas', 3, TRUE);

INSERT INTO producto_snack (id_categoria, nombre, descripcion, precio_actual, url_imagen, is_activo) VALUES
(1, 'Combo Pareja', '1 Cancha Gigante + 2 Gaseosas Medianas', 35.00, 'https://img.filmate.com/snacks/combo_pareja.png', TRUE),
(1, 'Combo Familiar', '2 Canchas Gigantes + 4 Gaseosas Medianas + 2 Nachos', 65.00, 'https://img.filmate.com/snacks/combo_fam.png', TRUE),
(3, 'Gaseosa Grande 32oz', 'Coca Cola, Sprite, Fanta o Inka Kola', 12.00, 'https://img.filmate.com/snacks/gaseosa_gde.png', TRUE);

INSERT INTO reserva_snack (id_reserva, id_producto, cantidad, precio_unitario) VALUES
(1, 1, 1, 35.00);
