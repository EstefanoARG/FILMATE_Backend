Instrucciones para generar la documentación (Sphinx)
==================================================

Requisitos (desde el entorno virtual del proyecto):

```powershell
python -m pip install -r docs/requirements-docs.txt
```

Generar la documentación:

```powershell
python scripts/build_docs.py

# abrir en Windows
start docs\_build\html\index.html
```

Notas:
- El comando `scripts/build_docs.py` ejecuta `sphinx-apidoc` para generar los archivos RST dentro de `docs/source/api/` y luego construye el HTML en `docs/_build/html/`.
- No se modifica el `README.md` del proyecto.
