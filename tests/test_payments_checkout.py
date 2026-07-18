from datetime import datetime, timedelta
from decimal import Decimal

from app.core.security import hash_password
from app.models.cinema import Cine
from app.models.movie import Pelicula
from app.models.room import Sala
from app.models.seat import Asiento
from app.models.showtime import Funcion
from app.models.showtime_seat import AsientoFuncion
from app.models.snack_category import CategoriaConfiteria
from app.models.snack_product import ProductoConfiteria
from app.models.transaccion import Transaccion
from app.models.user import Usuario


def _seed_checkout_context(db):
    user = Usuario(
        id_usuario=10,
        username="buyer",
        correo="buyer@filmate.test",
        contrasena=hash_password("Buyer123!"),
        nombre="Buyer",
        id_tipo_doc=1,
        numero_documento="76543210",
        estado_usuario="ACTIVO",
    )
    movie = Pelicula(
        id_pelicula=10,
        titulo="Pelicula Checkout",
        anio_lanzamiento=2026,
        duracion_minutos=120,
        clasificacion="APT",
        estado_pelicula="EN CARTELERA",
        url_poster="https://example.test/poster.jpg",
        director="QA Director",
    )
    cinema = Cine(
        id_cine=10,
        nombre_cine="Filmate QA",
        direccion="Av. Testing 123",
        horarios_apertura="Lunes a Domingo: 1:00 PM - 11:00 PM",
        estado_cine="Activo",
    )
    room = Sala(
        id_sala=10,
        id_cine=cinema.id_cine,
        nombre_sala="Sala QA",
        tipo_sala="Stand.",
        tipo_formato="2D",
        capacidad_asientos=2,
        estado_sala="Activa",
    )
    seat = Asiento(
        id_asiento=10,
        id_sala=room.id_sala,
        fila="A",
        columna=1,
        tipo_asiento="Regular",
        estado_asiento="Activo",
    )
    showtime = Funcion(
        id_funcion=10,
        id_pelicula=movie.id_pelicula,
        id_sala=room.id_sala,
        fecha_hora=datetime.now() + timedelta(days=1),
        precio_base=Decimal("15.00"),
    )
    category = CategoriaConfiteria(id_categoria_confi=10, nombre_categoria="Combos")
    product = ProductoConfiteria(
        id_producto=10,
        id_categoria_confi=category.id_categoria_confi,
        nombre_producto="Combo QA",
        descripcion="Combo de prueba",
        precio=Decimal("8.00"),
        url_imagen="https://example.test/combo.jpg",
        stock=5,
    )
    db.add_all([user, movie, cinema, room, seat, showtime, category, product])
    db.commit()
    return user, showtime, seat, product


def _tokenize_yape(client, celular="999111222", codigo_otp="123456"):
    response = client.post(
        "/client/payments/tokenize/yape",
        json={"celular": celular, "codigo_otp": codigo_otp},
    )
    assert response.status_code == 200
    return response.json()


def test_payment_test_methods_document_success_and_rejection_paths(client):
    response = client.get("/client/payments/metodos-prueba")

    assert response.status_code == 200
    data = response.json()
    assert data["yape_otp_valido"] == "123456"
    assert {"celular": "999111222", "resultado": "aprobado"} in data["yape"]
    assert {"celular": "999111000", "resultado": "rechazado"} in data["yape"]
    assert any(card["resultado"] == "rechazado" for card in data["tarjetas"])


def test_yape_tokenization_rejects_wrong_otp(client):
    tokenized = _tokenize_yape(client, codigo_otp="000000")

    assert tokenized["token"] is None
    assert "OTP" in tokenized["error"]


def test_checkout_approved_payment_creates_transaction_ticket_and_occupies_seat(client, db):
    user, showtime, seat, product = _seed_checkout_context(db)
    token = _tokenize_yape(client)["token"]

    response = client.post(
        "/client/orders/checkout",
        json={
            "id_usuario": user.id_usuario,
            "id_funcion": showtime.id_funcion,
            "ids_asientos": [seat.id_asiento],
            "snacks": [{"id_producto": product.id_producto, "cantidad": 1}],
            "token_pago": token,
            "email": user.correo,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["estado_pago"] == "Aprobado"
    assert data["monto_total"] == 23.0
    assert data["boletos"][0]["id_asiento"] == seat.id_asiento
    assert data["id_cargo_pasarela"].startswith("chr_")

    occupied = db.get(AsientoFuncion, (showtime.id_funcion, seat.id_asiento))
    assert occupied.estado == "Ocupado"
    assert db.query(Transaccion).count() == 1


def test_checkout_rejected_payment_is_atomic_and_does_not_occupy_seat(client, db):
    user, showtime, seat, _product = _seed_checkout_context(db)
    token = _tokenize_yape(client, celular="999111000")["token"]

    response = client.post(
        "/client/orders/checkout",
        json={
            "id_usuario": user.id_usuario,
            "id_funcion": showtime.id_funcion,
            "ids_asientos": [seat.id_asiento],
            "snacks": [],
            "token_pago": token,
            "email": user.correo,
        },
    )

    assert response.status_code == 402
    assert "Fondos insuficientes" in response.json()["detail"]
    assert db.get(AsientoFuncion, (showtime.id_funcion, seat.id_asiento)) is None
    assert db.query(Transaccion).count() == 0
