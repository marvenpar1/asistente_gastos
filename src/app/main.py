import json
import logging
import os
from datetime import date

import requests

from .llm import parse_movimiento
from .sheets import append_gasto  # luego lo puedes renombrar a append_movimiento

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "NOT_SET")


def lambda_handler(event, context):
    logger.info("=== Lambda handler iniciado ===")
    logger.info(
        "Entorno cargado: TELEGRAM_TOKEN=%s",
        "SET" if TELEGRAM_TOKEN != "NOT_SET" else "NOT_SET",
    )
    logger.info("Evento recibido: %s", json.dumps(event)[:500])

    try:
        if TELEGRAM_TOKEN == "NOT_SET":
            logger.error("TELEGRAM_BOT_TOKEN no está definido en las variables de entorno")

        # 1️⃣ Parsear el body que viene de Telegram (Function URL -> event["body"])
        body = json.loads(event.get("body", "{}"))
        message = body.get("message", {}).get("text", "")
        chat = body.get("message", {}).get("chat", {}) or {}
        chat_id = chat.get("id")

        logger.info("Body: %s", body)
        logger.info("Mensaje recibido: %s", message)
        logger.info("Chat ID: %s (tipo: %s)", chat_id, type(chat_id))

        if not message or not chat_id:
            logger.warning("No se encontró mensaje o chat_id en el evento")
            return {
                "statusCode": 200,
                "body": json.dumps({"ok": True, "skipped": True}),
            }

        # 2️⃣ Parsear con LLM: ahora queremos tipo = gasto/ingreso
        logger.info("Invocando parse_movimiento()...")
        movimiento = parse_movimiento(message)
        logger.info("Resultado parseo: %s", movimiento)

        # 3️⃣ Asegurar fecha
        if not movimiento.get("fecha"):
            movimiento["fecha"] = date.today().isoformat()
            logger.info("Fecha agregada automáticamente: %s", movimiento["fecha"])

        # 4️⃣ Quién (usar CHAT_ID_MARTA como env var)
        if str(chat_id) == os.environ.get("CHAT_ID_MARTA", ""):
            movimiento["quien"] = "Marta"
        else:
            movimiento["quien"] = "User2"

        # 5️⃣ Guardar en Google Sheets (incluyendo tipo)
        logger.info("Invocando append_gasto()...")
        append_gasto(movimiento)
        logger.info("✅ Movimiento registrado en Google Sheets")

        # 6️⃣ Responder en Telegram
        tipo = movimiento.get("tipo", "gasto")
        es_ingreso = (str(tipo).lower() == "ingreso")

        titulo = "Ingreso registrado ✅" if es_ingreso else "Gasto registrado ✅"
        signo = "+" if es_ingreso else "-"

        reply = (
            f"{titulo}\n"
            f"{signo}{movimiento['monto']} €\n"
            f"Categoría: {movimiento.get('categoria', 'N/A')}\n"
            f"Descripción: {movimiento.get('descripcion', 'N/A')}\n"
            f"Fecha: {movimiento['fecha']}\n"
            f"Quién: {movimiento['quien']}"
        )

        logger.info("Enviando respuesta a Telegram...")
        if TELEGRAM_TOKEN != "NOT_SET":
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": reply},
                timeout=5,
            )
        else:
            logger.error("No se envía mensaje a Telegram porque falta TELEGRAM_BOT_TOKEN")

        logger.info("✅ Mensaje enviado a Telegram (o saltado por falta de token)")

        return {"statusCode": 200, "body": json.dumps({"ok": True})}

    except Exception:
        logger.exception("❌ Error en lambda_handler")
        # Telegram solo necesita 200; le devolvemos error lógico pero HTTP 200
        return {"statusCode": 200, "body": json.dumps({"ok": False, "error": True})}