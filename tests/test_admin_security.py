from app.core.security import create_access_token, hash_password
from app.models.permiso import Permiso
from app.models.role import Rol
from app.models.rol_permiso import RolPermiso
from app.models.user import Usuario
from app.models.usuario_rol import UsuarioRol


def _headers(user_id, roles):
    return {"Authorization": f"Bearer {create_access_token(user_id, roles)}"}


def _seed_admin_user(db, role_id=1, permiso_codigo="GESTIONAR_PELICULAS"):
    user = Usuario(
        id_usuario=100 + role_id,
        username=f"admin{role_id}",
        correo=f"admin{role_id}@filmate.test",
        contrasena=hash_password("Admin123!"),
        nombre=f"Admin {role_id}",
        id_tipo_doc=1,
        numero_documento=f"9000000{role_id}",
        estado_usuario="ACTIVO",
    )
    role = Rol(id_role=role_id, nombre_rol="SUPERADMIN" if role_id == 3 else "ADMINISTRADOR")
    permiso = Permiso(codigo_permiso=permiso_codigo, descripcion="Permiso de prueba", modulo="TEST")
    db.add_all([user, role, permiso])
    db.flush()
    db.add_all([
        UsuarioRol(id_usuario=user.id_usuario, id_role=role.id_role),
        RolPermiso(id_role=role.id_role, id_permiso=permiso.id_permiso),
    ])
    db.commit()
    return user


def test_admin_endpoint_requires_token(client):
    response = client.get("/admin/movies/")

    assert response.status_code == 401
    assert response.json()["detail"] == "Token requerido"


def test_client_role_cannot_access_admin_movies(client, db):
    user = Usuario(
        id_usuario=200,
        username="clientrole",
        correo="clientrole@filmate.test",
        contrasena=hash_password("Client123!"),
        nombre="Client Role",
        id_tipo_doc=1,
        numero_documento="92000000",
        estado_usuario="ACTIVO",
    )
    db.add_all([user, Rol(id_role=2, nombre_rol="CLIENTE")])
    db.add(UsuarioRol(id_usuario=user.id_usuario, id_role=2))
    db.commit()

    response = client.get("/admin/movies/", headers=_headers(user.id_usuario, [2]))

    assert response.status_code == 403
    assert "administrador" in response.json()["detail"].lower()


def test_admin_with_required_permission_can_list_movies(client, db):
    admin = _seed_admin_user(db, role_id=1, permiso_codigo="GESTIONAR_PELICULAS")

    response = client.get("/admin/movies/", headers=_headers(admin.id_usuario, [1]))

    assert response.status_code == 200
    assert response.json() == []


def test_superadmin_can_access_superadmin_routes(client, db):
    superadmin = _seed_admin_user(db, role_id=3, permiso_codigo="GESTIONAR_PELICULAS")

    response = client.get("/admin/roles/", headers=_headers(superadmin.id_usuario, [3]))

    assert response.status_code == 200
    assert any(role["nombre_rol"] == "SUPERADMIN" for role in response.json())


def test_admin_cannot_access_superadmin_routes(client, db):
    admin = _seed_admin_user(db, role_id=1, permiso_codigo="GESTIONAR_PELICULAS")

    response = client.get("/admin/roles/", headers=_headers(admin.id_usuario, [1]))

    assert response.status_code == 403
    assert "superadmin" in response.json()["detail"].lower()
