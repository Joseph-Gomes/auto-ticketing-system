from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from config import Config


def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        Config.SERVICE_JSON,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)


def add_ticket(ticket):
    service = get_sheets_service()
    sheet = service.spreadsheets()
    spreadsheet_id = Config.SHEET_ID
    sheet_name = Config.SHEET_NAME

    ticket_id = f"T-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    row = [
        ticket_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ticket.get("from", "Unknown"),
        ticket.get("subject", "No Subject"),
        "Open"
    ]

    sheet.values().append(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A:E",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]}
    ).execute()

    print(f"✅ Ticket added to Google Sheet: {ticket_id}")
    return ticket_id


def fetch_all_tickets():
    creds = service_account.Credentials.from_service_account_file(
        Config.SERVICE_JSON,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build("sheets", "v4", credentials=creds)

    spreadsheet_id = Config.SHEET_ID
    sheet_name = Config.SHEET_NAME
    range_name = f"{sheet_name}!A:E"

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name
    ).execute()

    values = result.get("values", [])

    if not values or len(values) < 2:
        return []

    headers = values[0]
    rows = values[1:]
    tickets = []

    for row in rows:
        ticket = {}
        for i, header in enumerate(headers):
            if i < len(row):
                ticket[header.lower()] = row[i]
        tickets.append(ticket)

    return tickets
