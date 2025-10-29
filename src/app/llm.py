import json
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

import dotenv
import google.generativeai as gen

dotenv.load_dotenv()
gen.configure(api_key=os.environ["GEMINI_API_KEY"])
print(os.environ["GEMINI_API_KEY"])
TZ = ZoneInfo("America/Bogota")

MODEL = "models/gemini-2.0-flash"

SYSTEM_PROMPT = """
Eres un extractor de información. Devuelves SOLO JSON válido, sin texto adicional, sin ```.

El JSON DEBE ser exactamente este:
{
  "monto": float,
  "categoria": string,
  "descripcion": string,
  "fecha": "YYYY-MM-DD" | null
}

Reglas:
- NO inventes fechas.
- Si el usuario NO menciona una fecha explícita (o relativa), devuelve "fecha": null.
- Categorías permitidas: servicios domesticos, gastos, comida, transporte, mercado, ocio, salud, otros.
- No incluyas comentarios, explicaciones ni texto fuera del JSON.
"""

def parse_gasto(texto):
    prompt = SYSTEM_PROMPT + "\nUsuario: " + texto

    response = gen.GenerativeModel(
        MODEL,
        generation_config={
            "response_mime_type": "application/json"   # <-- LA CLAVE
        },
    ).generate_content(prompt)

    data = json.loads(response.text)

    # Set default date
    if not data.get("fecha"):
        data["fecha"] = date.today().isoformat()

    return data