import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()


class Config:
    # --------------------------
    # 📧 Gmail / IMAP Settings
    # --------------------------
    EMAIL = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
    IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")

    # --------------------------
    # 📊 Google Sheets / Service Account
    # --------------------------
    # Dynamically choose the correct JSON path:
    SERVICE_JSON = (
        "/etc/secrets/google_service_account.json"
        if os.path.exists("/etc/secrets/google_service_account.json")
        else os.path.join(os.path.dirname(__file__), "credentials", "google_service_account.json")
    )

    SHEET_ID = os.getenv("SHEET_ID", "1eYLJZ0fKVfvn0Rg1NEb3cRB7S9c1mi0J35ARiUBQyjw")
    SHEET_NAME = os.getenv("SHEET_NAME", "Ticket Log")

    # --------------------------
    # ⚙️ App Configuration
    # --------------------------
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SECONDS", 300))
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")

    # --------------------------
    # 🪵 Logging
    # --------------------------
    LOG_FILE = os.path.join(os.getcwd(), "automation.log")
