import uuid

# Pasarela de pago SIMULADA para demo/pruebas: no llama a ningún proveedor externo.
# Los "tokens" viven solo en memoria del proceso (se pierden si el server reinicia),
# igual que un token real de un solo uso: se generan al "tokenizar" una tarjeta/Yape
# de prueba y se consumen al cobrar.

TARJETAS_PRUEBA = {
    "4551700000000004": {"marca": "Visa", "resultado": "aprobado", "mensaje": "Pago aprobado"},
    "5301700000000006": {"marca": "Mastercard", "resultado": "aprobado", "mensaje": "Pago aprobado"},
    "4551700000000012": {"marca": "Visa", "resultado": "rechazado", "mensaje": "Fondos insuficientes"},
    "4551700000000020": {"marca": "Visa", "resultado": "rechazado", "mensaje": "Tarjeta inválida"},
    "4551700000000038": {"marca": "Visa", "resultado": "rechazado", "mensaje": "Tarjeta vencida"},
}

YAPE_NUMEROS_PRUEBA = {
    "999111222": {"resultado": "aprobado", "mensaje": "Pago aprobado"},
    "999111000": {"resultado": "rechazado", "mensaje": "Fondos insuficientes"},
}
YAPE_OTP_VALIDO = "123456"

_tokens: dict = {}


def listar_metodos_prueba() -> dict:
    return {
        "tarjetas": [
            {"numero": numero, "marca": info["marca"], "cvv": "123", "vencimiento": "11/30", "resultado": info["resultado"]}
            for numero, info in TARJETAS_PRUEBA.items()
        ],
        "yape": [
            {"celular": celular, "resultado": info["resultado"]}
            for celular, info in YAPE_NUMEROS_PRUEBA.items()
        ],
        "yape_otp_valido": YAPE_OTP_VALIDO,
    }


def tokenizar_tarjeta(numero_tarjeta: str, cvv: str, mes_expiracion: int, anio_expiracion: int, titular: str) -> dict:
    numero = numero_tarjeta.replace(" ", "")
    info = TARJETAS_PRUEBA.get(numero)
    if not info:
        return {"token": None, "marca": None, "error": "Tarjeta no reconocida. Usá una tarjeta de prueba (GET /client/payments/metodos-prueba)."}

    token = f"tok_{uuid.uuid4().hex}"
    _tokens[token] = {
        "metodo_pago": info["marca"],
        "aprobado": info["resultado"] == "aprobado",
        "mensaje": info["mensaje"],
    }
    return {"token": token, "marca": info["marca"], "error": None}


def tokenizar_yape(celular: str, codigo_otp: str) -> dict:
    if codigo_otp != YAPE_OTP_VALIDO:
        return {"token": None, "error": "Código OTP incorrecto"}

    info = YAPE_NUMEROS_PRUEBA.get(celular)
    if not info:
        return {"token": None, "error": "Número no reconocido. Usá un número de prueba (GET /client/payments/metodos-prueba)."}

    token = f"tok_{uuid.uuid4().hex}"
    _tokens[token] = {
        "metodo_pago": "Yape",
        "aprobado": info["resultado"] == "aprobado",
        "mensaje": info["mensaje"],
    }
    return {"token": token, "error": None}


def cobrar(token: str, monto_soles: float, email: str) -> dict:
    """Token de un solo uso: se consume acá para que no se pueda reusar en otro checkout."""
    info = _tokens.pop(token, None)
    if not info:
        return {"aprobado": False, "id_cargo": None, "mensaje": "Token inválido o ya utilizado", "metodo_pago": None}

    if not info["aprobado"]:
        return {"aprobado": False, "id_cargo": None, "mensaje": info["mensaje"], "metodo_pago": info["metodo_pago"]}

    return {
        "aprobado": True,
        "id_cargo": f"chr_{uuid.uuid4().hex[:16]}",
        "mensaje": info["mensaje"],
        "metodo_pago": info["metodo_pago"],
    }
