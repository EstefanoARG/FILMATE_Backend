# Demo en vivo - Proyecto Integrador de Pruebas

## Guion sugerido de 4 a 6 minutos

1. Mostrar el sistema FILMATE y explicar los flujos criticos:
   - Login y roles.
   - Gestion admin.
   - Compra de entrada.
   - Social/favoritos.

2. Ejecutar smoke test:

```powershell
cd FILMATE_Backend
.\venv\Scripts\python.exe -m pytest tests/test_app.py -q
```

3. Ejecutar seguridad RBAC:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_admin_security.py -q
```

4. Ejecutar checkout y pagos:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_payments_checkout.py -q
```

5. Ejecutar suite completa con cobertura:

```powershell
.\venv\Scripts\python.exe -m pytest --cov=app --cov-report=term-missing --cov-report=xml -q
```

6. Mostrar evidencia:
   - `coverage.xml`
   - salida de terminal con tests pasando
   - matriz en `docs/calidad/matriz_casos_prueba.md`

## Flujo representativo para defender

Pago aprobado:
- Tokenizar Yape con `999111222` y OTP `123456`.
- Enviar checkout con asiento.
- Validar transaccion, ticket y asiento ocupado.

Pago rechazado:
- Tokenizar Yape con `999111000` y OTP `123456`.
- Enviar checkout.
- Validar HTTP 402 y que no se crea transaccion ni asiento ocupado.

Este flujo demuestra prueba basada en riesgo y consistencia transaccional.

