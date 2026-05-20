"""Paquete de modelos de la aplicación.

Aquí se exportan las clases ORM para que la API y Sphinx puedan importarlas
como `app.models.<Clase>`.
"""

from .role import Rol
from .user import Usuario
from .movie import Pelicula
from .genre import Genero
from .movie_genre import PeliculaGenero
from .actor import Actor
from .movie_actor import PeliculaActor
from .banner import BannerHome
from .review import Resena
from .favorite import Favorito
from .cinema import Cine
from .room import Sala
from .seat import Asiento
from .showtime import Funcion
from .showtime_seat import FuncionAsiento
from .tariff import Tarifa
from .promotion import Promocion
from .snack_category import CategoriaSnack
from .snack_product import ProductoSnack
from .reservation import Reserva
from .reservation_snack import ReservaSnack
from .ticket import Boleto