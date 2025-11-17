import json
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo
import google.generativeai as gen

TZ = ZoneInfo("America/Bogota")
MODEL = "models/gemini-2.0-flash"


def _configure_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Lanzamos un error CLARO si falta la API key
        raise RuntimeError("GEMINI_API_KEY no está definida en las variables de entorno")
    gen.configure(api_key=api_key)


SYSTEM_PROMPT_MOVIMIENTO = """
Eres un extractor de información financiera personal. Devuelves SOLO JSON válido, sin texto adicional, sin ```.

El JSON DEBE ser exactamente este:
{
  "monto": float,
  "categoria": string,
  "descripcion": string,
  "fecha": "YYYY-MM-DD" | null,
  "tipo": "gasto" | "ingreso"
}

Reglas:
- "tipo" debe ser:
  - "gasto" cuando el usuario está pagando, gastando, comprando, transfiriendo dinero que sale de su bolsillo.
  - "ingreso" cuando el usuario está recibiendo dinero, cobrando, le ingresan dinero.
- NO inventes fechas.
- Si el usuario NO menciona una fecha explícita (o relativa), devuelve "fecha": null.
- Categorías permitidas: servicios domesticos, gastos, comida, transporte, mercado, ocio, salud, otros, ingresos.
- "monto" siempre número decimal (sin símbolo €).
- "descripcion" frase corta.
- No incluyas nada fuera del JSON.
"""


def _generate_json(prompt: str) -> dict:
    _configure_gemini()  # configuramos justo antes de llamar
    response = gen.GenerativeModel(
        MODEL,
        generation_config={"response_mime_type": "application/json"},
    ).generate_content(prompt)

    data = json.loads(response.text)
    return data


def parse_movimiento(texto: str) -> dict:
    prompt = SYSTEM_PROMPT_MOVIMIENTO + "\nUsuario: " + texto
    data = _generate_json(prompt)

    from datetime import date

    if not data.get("fecha"):
        data["fecha"] = date.today().isoformat()

    tipo = (data.get("tipo") or "gasto").lower().strip()
    if tipo not in ("gasto", "ingreso"):
        tipo = "gasto"
    data["tipo"] = tipo

    return data