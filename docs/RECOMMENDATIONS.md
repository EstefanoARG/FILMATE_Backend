# Motor de Recomendación Inteligente — Documentación de Integración

> **RF:** F-03 (Recomendación Inteligente)
> **HU:** HU-SOC-04 (Recomendación Inteligente de Películas)
> **Tag OpenAPI:** `recommendations`
> **Endpoint:** `GET /api/recommendations/home`

Este documento describe qué se agregó al backend, el contrato HTTP del endpoint y cómo el frontend debe consumirlo para alimentar el carrusel de inicio.

---

## 1. ¿Qué se agregó en el backend?

### 1.1 Archivos nuevos

| Archivo | Responsabilidad |
| --- | --- |
| `app/schemas/recommendation.py` | Esquemas Pydantic: `PeliculaRecomendada`, `RecommendationResponse`, `RecommendationSignals`, `GeneroSimple`. |
| `app/repositories/recommendation_repository.py` | Consultas SQL parametrizadas que extraen las tres señales del usuario y rankean candidatas. |
| `app/services/recommendation_service.py` | Lógica de negocio. Expone `get_personalized_recommendations(user_id, limit, db)` (`async`). |
| `app/routes/client_recommendations.py` | Endpoint HTTP `GET /api/recommendations/home` con `get_current_user` + `get_db`. |

### 1.2 Archivos modificados

| Archivo | Cambio |
| --- | --- |
| `app/core/dependencies.py` | Nueva dependencia `get_current_user` (valida JWT y devuelve `user_id` + `roles`; no restringe por rol). |
| `app/core/app.py` | Importa y registra `client_recommendations.router`, y agrega el tag `recommendations` en `tags_metadata`. |

### 1.3 Algoritmo (resumen)

El motor combina tres señales del usuario autenticado:

1. **Películas favoritas** → `interacciones_peliculas.favorita = 1`.
2. **Directores clave** → directores de películas que el usuario calificó con **5 estrellas** (`resenas.puntuacion_estrellas = 5`).
3. **Géneros más consumidos** → top 3 géneros por número de compras confirmadas (`transacciones` → `funciones` → `peliculas_generos`).

**Score por película candidata** (mayor = más relevante):

| Componente | Peso |
| --- | --- |
| Comparte director con los "directores clave" | **+5.0** |
| Cada género que coincide con un top-género comprado (cap. 4 hits) | **+2.0 × hits** |
| Cada género presente en las favoritas del usuario (cap. 3 hits) | **+1.0 × hits** |
| Bonus de comunidad | `log(1 + total_favoritos_comunidad) × 0.1` |

**Exclusiones obligatorias:** `eliminado = 1`, favoritas y vistas del usuario (`interacciones_peliculas.vista = 1`).

**Fallback:** si el usuario no tiene historial suficiente, se completa con películas populares en cartelera (`total_favoritos_comunidad DESC`).

**Orden de ranking (desempates):** `score desc → total_favoritos_comunidad desc → promedio_resenas desc → id_pelicula desc`.

---

## 2. Contrato HTTP

### 2.1 Request

```http
GET /api/recommendations/home?limit=10
Host: <host-api>
Authorization: Bearer <jwt>
```

| Header / Query | Tipo | Requerido | Descripción |
| --- | --- | --- | --- |
| `Authorization` | `string` | **Sí** | Token JWT emitido por `/auth/login`. |
| `limit` | `int` (1–50, default `10`) | No | Cantidad máxima de sugerencias devueltas. |

**Códigos de error:**

| Status | Causa | `detail` |
| --- | --- | --- |
| `401` | Sin token | `"Token requerido"` |
| `401` | Token inválido/expirado | `"Token inválido o expirado"` |
| `401` | Token sin `user_id` | `"Token malformado"` |
| `400` | `user_id` inválido | `"Token sin user_id válido"` |
| `500` | Fallo en BD / inesperado | `"No fue posible calcular las recomendaciones"` |

### 2.2 Response (200)

```json
{
  "user_id": 42,
  "total": 3,
  "recomendaciones": [
    {
      "id_pelicula": 101,
      "titulo": "Dune: Part Two",
      "url_poster": "https://cdn.filmate.app/posters/dune2.jpg",
      "url_banner": "https://cdn.filmate.app/banners/dune2.jpg",
      "director": "Denis Villeneuve",
      "anio_lanzamiento": 2024,
      "clasificacion": "PG-13",
      "duracion_minutos": 166,
      "estado_pelicula": "EN_CARTELERA",
      "promedio_resenas": 4.6,
      "total_resenas": 1280,
      "total_favoritos_comunidad": 5231,
      "generos": [
        { "id_genero": 1, "nombre_genero": "Ciencia Ficción" },
        { "id_genero": 4, "nombre_genero": "Drama" }
      ],
      "score": 9.31,
      "score_director": 5.0,
      "score_genero_top": 4.0,
      "score_genero_favorito": 0.0,
      "motivo": "Porque es de un director que sigues y del género Ciencia Ficción que más consumes"
    }
  ],
  "signals": {
    "peliculas_favoritas_count": 12,
    "peliculas_vistas_count": 47,
    "resenas_5_estrellas_count": 9,
    "directores_clave_count": 4,
    "top_generos_count": 3,
    "compras_analizadas": 23
  }
}
```

### 2.3 Campos de cada película recomendada

| Campo | Tipo | Descripción para el carrusel |
| --- | --- | --- |
| `id_pelicula` | `int` | ID para navegar al detalle (`/movies/{id}`). |
| `titulo` | `string` | Título visible. |
| `url_poster` | `string` | Imagen principal del card. |
| `url_banner` | `string\|null` | Banner opcional (modo hero). |
| `director` | `string` | Subtítulo del card. |
| `anio_lanzamiento` | `int` | Año (badge secundario). |
| `clasificacion` | `string\|null` | Clasificación por edad. |
| `duracion_minutos` | `int\|null` | Duración. |
| `estado_pelicula` | `string\|null` | Estado de exhibición. |
| `promedio_resenas` | `float` | Rating promedio. |
| `total_resenas` | `int` | Cantidad de reseñas. |
| `total_favoritos_comunidad` | `int` | Popularidad (badge "Popular"). |
| `generos` | `GeneroSimple[]` | Chips de género. |
| `score` | `float` | Score interno (opcional, útil para debug). |
| `score_director` | `float` | Sub-score por director. |
| `score_genero_top` | `float` | Sub-score por género top. |
| `score_genero_favorito` | `float` | Sub-score por género favorito. |
| `motivo` | `string\|null` | Texto listo para mostrar como tooltip/subtítulo ("Porque es…"). |

> Los sub-scores y `motivo` **pueden omitirse visualmente** si no se desea exponer la lógica; el resto de campos basta para renderizar el carrusel.

---

## 3. Cómo consumirlo desde el frontend

### 3.1 Cliente HTTP recomendado

```ts
// services/recommendations.ts
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type GeneroSimple = { id_genero: number; nombre_genero: string };

export type PeliculaRecomendada = {
  id_pelicula: number;
  titulo: string;
  url_poster: string;
  url_banner: string | null;
  director: string;
  anio_lanzamiento: number;
  clasificacion: string | null;
  duracion_minutos: number | null;
  estado_pelicula: string | null;
  promedio_resenas: number;
  total_resenas: number;
  total_favoritos_comunidad: number;
  generos: GeneroSimple[];
  score: number;
  score_director: number;
  score_genero_top: number;
  score_genero_favorito: number;
  motivo: string | null;
};

export type RecommendationResponse = {
  user_id: number;
  total: number;
  recomendaciones: PeliculaRecomendada[];
  signals: {
    peliculas_favoritas_count: number;
    peliculas_vistas_count: number;
    resenas_5_estrellas_count: number;
    directores_clave_count: number;
    top_generos_count: number;
    compras_analizadas: number;
  } | null;
};

export async function getHomeRecommendations(
  token: string,
  limit = 10,
  signal?: AbortSignal
): Promise<RecommendationResponse> {
  const res = await fetch(
    `${API_BASE}/api/recommendations/home?limit=${limit}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
      },
      signal,
    }
  );

  if (!res.ok) {
    // 401 -> token expirado; 500 -> fallback
    throw new Error(`recommendations_error_${res.status}`);
  }
  return res.json();
}
```

### 3.2 Hook de React (ejemplo)

```tsx
// hooks/useHomeRecommendations.ts
import { useEffect, useState } from "react";
import { getHomeRecommendations, type PeliculaRecomendada } from "@/services/recommendations";
import { useAuth } from "@/hooks/useAuth"; // tu hook actual de sesión

export function useHomeRecommendations(limit = 10) {
  const { token } = useAuth();
  const [data, setData] = useState<PeliculaRecomendada[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    const ctrl = new AbortController();
    setLoading(true);
    getHomeRecommendations(token, limit, ctrl.signal)
      .then((res) => setData(res.recomendaciones))
      .catch((e) => {
        if (e.name !== "AbortError") setError(String(e));
        setData([]); // el front debe tener su propio fallback
      })
      .finally(() => setLoading(false));
    return () => ctrl.abort();
  }, [token, limit]);

  return { data, loading, error };
}
```

### 3.3 Render del carrusel

```tsx
// components/HomeRecommendationsCarousel.tsx
import { useHomeRecommendations } from "@/hooks/useHomeRecommendations";

export function HomeRecommendationsCarousel() {
  const { data, loading, error } = useHomeRecommendations(10);

  if (loading) return <CarrouselSkeleton />;
  if (error || data.length === 0) return null; // fallback a "Tendencias"

  return (
    <section aria-label="Recomendado para ti">
      <h2>Recomendado para ti</h2>
      <div className="carousel">
        {data.map((peli) => (
          <article key={peli.id_pelicula} className="movie-card">
            <img src={peli.url_poster} alt={peli.titulo} loading="lazy" />
            <h3>{peli.titulo}</h3>
            <p className="director">{peli.director} · {peli.anio_lanzamiento}</p>
            {peli.motivo && <p className="motivo">{peli.motivo}</p>}
            <div className="generos">
              {peli.generos.map((g) => (
                <span key={g.id_genero} className="chip">{g.nombre_genero}</span>
              ))}
            </div>
            <span className="rating">★ {peli.promedio_resenas.toFixed(1)}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
```

### 3.4 Buenas prácticas

- **Cachea por usuario** la respuesta durante 5–10 minutos (clave: `user_id + limit`). Las señales no cambian en milisegundos.
- **Limpia el cache al cerrar sesión** y al ejecutar acciones que afectan las señales: marcar favorita, marcar vista, dejar reseña con 5★, completar compra.
- **Maneja `401` redirigiendo al login**; el middleware `get_current_user` rechaza cualquier token inválido/expirado.
- **Maneja el array vacío** mostrando un carrusel alternativo (ej. "Tendencias" o "En cartelera"). El backend ya devuelve fallback interno para historial pobre, pero el front debe seguir contando con un plan B.
- **Respeta `signal: AbortController`** para no setear estado tras desmontar el componente.
- **`limit` recomendado:** 10 para desktop, 6 para mobile.

---

## 4. Pruebas rápidas

```bash
# 1) Levantar backend
uvicorn app.main:app --reload

# 2) Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"correo":"user@example.com","contrasena":"Test1234!"}'

# 3) Consumir recomendaciones
curl http://localhost:8000/api/recommendations/home?limit=10 \
  -H "Authorization: Bearer <TOKEN>"
```

Ver también: Swagger UI en `http://localhost:8000/api/docs` → tag **recommendations**.

---

## 5. Checklist de integración frontend

- [ ] Servicio HTTP con `Authorization: Bearer <token>`.
- [ ] Hook que cancele requests con `AbortController`.
- [ ] Renderizado del carrusel con `url_poster`, `titulo`, `director`, `generos`, `promedio_resenas`.
- [ ] Cache por `user_id` con invalidación tras acciones que cambian señales.
- [ ] Estado vacío → carrusel alternativo.
- [ ] 401 → re-login.
- [ ] Accesibilidad: `alt` en pósters, `aria-label` en la sección.
