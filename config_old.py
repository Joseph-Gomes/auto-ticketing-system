import os

class Config:
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "autoticketingproject@gmail.com")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "kynarwqxnmlphfsu")
    SHEET_ID = os.getenv("SHEET_ID", "1eYLJZ0fKVfvn0Rg1NEb3cRB7S9c1mi0J35ARiUBQyjw")
    SHEET_NAME = "Ticket Log"  # ✅ Added this
    SECRET_KEY = "your_secret_key_here"
    SERVICE_JSON = os.path.join(os.path.dirname(__file__), "credentials", "google_service_account.json")

    LOG_FILE = os.path.join(os.getcwd(), "automation.log")

    IMAP_SERVER = "imap.gmail.com"
    SMTP_SERVER = "smtp.gmail.com"
