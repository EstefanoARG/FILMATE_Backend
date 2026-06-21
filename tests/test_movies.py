from datetime import datetime, timezone


def _create_test_movie(db):
    from app.models.movie import Pelicula
    from app.models.genre import Genero

    genre = Genero(nombre_genero="Acción")
    db.add(genre)
    db.flush()

    movie = Pelicula(
        titulo="Test Movie",
        sinopsis="A test movie",
        anio_lanzamiento=2026,
        duracion_minutos=120,
        clasificacion="PG-13",
        estado_pelicula="Activo",
        url_poster="http://example.com/poster.jpg",
        url_trailer="http://example.com/trailer.mp4",
        director="Test Director",
    )
    db.add(movie)
    db.flush()
    db.commit()
    return movie.id_pelicula


def test_list_movies(client, db):
    _create_test_movie(db)
    response = client.get("/client/movies/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(m["titulo"] == "Test Movie" for m in data)


def test_list_movies_empty(client):
    response = client.get("/client/movies/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_movie_not_found(client):
    response = client.get("/client/movies/99999")
    assert response.status_code == 404


def test_search_movies(client, db):
    _create_test_movie(db)
    response = client.get("/client/movies/search", params={"q": "Test"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_search_movies_no_match(client):
    response = client.get("/client/movies/search", params={"q": "NonExistentMovie"})
    assert response.status_code == 200
    assert response.json() == []
