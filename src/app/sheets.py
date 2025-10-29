import base64
import json
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build


def get_google_credentials():
    creds_b64 = os.getenv("GOOGLE_CREDENTIALS_JSON_BASE64")
    if not creds_b64:
        raise RuntimeError("Missing GOOGLE_CREDENTIALS_JSON_BASE64")

    creds_json = base64.b64decode(creds_b64).decode("utf-8")
    creds_dict = json.loads(creds_json)
    return service_account.Credentials.from_service_account_info(creds_dict)

def append_gasto(gasto):
    creds = get_google_credentials()
    service = build("sheets", "v4", credentials=creds)

    values = [[gasto["fecha"], gasto["monto"], gasto["categoria"], gasto["descripcion"], gasto["quien"]]]
    body = {"values": values}

    SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range="registros!A:D",
        valueInputOption="USER_ENTERED",
        body=body,
    ).execute()
