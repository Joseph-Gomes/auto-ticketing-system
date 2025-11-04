from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    EMAIL = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
    IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")  # Add this too
    SERVICE_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials/google_service_account.json")
    SHEET_ID = os.getenv("SHEET_ID", "1eYLJZ0fKVfvn0Rg1NEb3cRB7S9c1mi0J35ARiUBQyjw")
    SHEET_NAME = os.getenv("SHEET_NAME", "Ticket Log")
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", 300))
