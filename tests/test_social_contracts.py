from app.core.security import hash_password
from app.models.coleccion import Coleccion
from app.models.coleccion_pelicula import ColeccionPelicula
from app.models.interaccion_pelicula import InteraccionPelicula
from app.models.movie import Pelicula
from app.models.seguidor import Seguidor
from app.models.user import Usuario


def _seed_users_and_movie(db):
    user = Usuario(
        id_usuario=31,
        username="social_user",
        correo="social_user@filmate.test",
        contrasena=hash_password("Social123!"),
        nombre="Social User",
        id_tipo_doc=1,
        numero_documento="31000001",
        estado_usuario="ACTIVO",
    )
    followed = Usuario(
        id_usuario=32,
        username="followed_user",
        correo="followed_user@filmate.test",
        contrasena=hash_password("Social123!"),
        nombre="Followed User",
        id_tipo_doc=1,
        numero_documento="32000001",
        estado_usuario="ACTIVO",
    )
    movie = Pelicula(
        id_pelicula=31,
        titulo="Social Contract Movie",
        anio_lanzamiento=2026,
        duracion_minutos=100,
        clasificacion="APT",
        estado_pelicula="EN CARTELERA",
        url_poster="https://example.test/social.jpg",
        director="Social Director",
    )
    db.add_all([user, followed, movie])
    db.commit()
    return user, followed, movie


def test_user_interactions_embed_movie_to_avoid_frontend_n_plus_one(client, db):
    user, _followed, movie = _seed_users_and_movie(db)
    db.add(
        InteraccionPelicula(
            id_usuario=user.id_usuario,
            id_pelicula=movie.id_pelicula,
            vista=True,
            favorita=True,
            en_lista_seguimiento=False,
        )
    )
    db.commit()

    response = client.get(f"/interacciones/usuario/{user.id_usuario}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id_pelicula"] == movie.id_pelicula
    assert data[0]["pelicula"]["titulo"] == movie.titulo
    assert data[0]["pelicula"]["url_poster"] == movie.url_poster


def test_following_endpoint_embeds_followed_profile(client, db):
    user, followed, _movie = _seed_users_and_movie(db)
    db.add(Seguidor(id_seguidor=user.id_usuario, id_seguido=followed.id_usuario))
    db.commit()

    response = client.get(f"/client/seguidores/{user.id_usuario}/siguiendo")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id_seguido"] == followed.id_usuario
    assert data[0]["seguido"]["username"] == followed.username


def test_collection_details_return_movies_in_single_response(client, db):
    user, _followed, movie = _seed_users_and_movie(db)
    collection = Coleccion(
        id_usuario=user.id_usuario,
        titulo_coleccion="Favoritas QA",
        descripcion="Coleccion de prueba",
    )
    db.add(collection)
    db.flush()
    db.add(ColeccionPelicula(id_coleccion=collection.id_coleccion, id_pelicula=movie.id_pelicula))
    db.commit()

    response = client.get(f"/client/colecciones/usuario/{user.id_usuario}/detalles")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["titulo_coleccion"] == "Favoritas QA"
    assert data[0]["peliculas"] == [
        {
            "id_pelicula": movie.id_pelicula,
            "titulo": movie.titulo,
            "url_poster": movie.url_poster,
        }
    ]
