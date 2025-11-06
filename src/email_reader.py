import imaplib
import email
from email.header import decode_header
from config import Config
from dotenv import load_dotenv
import os
import time
import logging
import sys
import re
from ticket_manager import add_ticket
from email_sender import send_auto_reply  # Send confirmation email

# Load environment variables
load_dotenv()

# --- Logging Configuration ---
LOG_FILE = "automation.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Also print logs to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)


# -------------------------------
# ✉️ Helper: Decode MIME & Extract Sender
# -------------------------------
def decode_mime_words(header_value):
    """Decode MIME-encoded email headers (e.g., =?UTF-8?...)."""
    if not header_value:
        return ""
    decoded_parts = decode_header(header_value)
    return ''.join(
        part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
        for part, charset in decoded_parts
    )


def extract_sender(from_header):
    """
    Extract sender in 'Name (email@example.com)' format.
    Handles:
    - John Doe <email@example.com>
    - email@example.com
    """
    if not from_header:
        return "Unknown"

    match = re.match(r'(.*)<(.+@.+)>', from_header)
    if match:
        name = match.group(1).strip().strip('"')
        email_addr = match.group(2).strip()
        if name:
            return f"{name} ({email_addr})"
        else:
            return email_addr
    else:
        return from_header.strip()


# -------------------------------
# 📥 Connect to Gmail
# -------------------------------
def connect_to_mailbox():
    """Connect to Gmail via IMAP using credentials from .env"""
    logging.info("Connecting to Gmail IMAP server...")
    try:
        mail = imaplib.IMAP4_SSL(Config.IMAP_SERVER)
        mail.login(Config.EMAIL, Config.EMAIL_PASSWORD)
        logging.info(f"Logged in successfully as: {Config.EMAIL}")
        mail.select("inbox")
        return mail
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP login failed: {e}")
        return None


# -------------------------------
# 📧 Process Inbox
# -------------------------------
def check_inbox(mail):
    """Check inbox for unread emails, create tickets, and send confirmation replies."""
    status, messages = mail.search(None, "UNSEEN")
    if status != "OK":
        logging.error("Error searching inbox.")
        return

    email_ids = messages[0].split()
    logging.info(f"Found {len(email_ids)} new unread emails.")

    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        # Decode subject safely
        subject = decode_mime_words(msg["Subject"])
        raw_from = decode_mime_words(msg["From"])
        sender = extract_sender(raw_from)

        logging.info(f"Processing Email: {subject} (From: {sender})")

        # Prepare ticket data
        ticket_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "subject": subject,
            "from": sender,
            "status": "New",
        }

        # Add to Google Sheet and send confirmation
        try:
            ticket_id = add_ticket(ticket_data)
            logging.info(f"✅ Ticket added to sheet: {ticket_id}")

            send_auto_reply(sender, subject, ticket_id)
        except Exception as e:
            logging.error(f"❌ Failed to process '{subject}': {e}")

        # Mark as read
        mail.store(e_id, "+FLAGS", "\\Seen")

    logging.info("All unread emails processed.\n")


# -------------------------------
# ⏱ Countdown Timer
# -------------------------------
def countdown(seconds):
    """Show live countdown timer in terminal"""
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\r⏳ Next check in: {remaining:3d}s ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r🔄 Checking inbox again...           \n")
    sys.stdout.flush()


# -------------------------------
# ▶️ Main Loop
# -------------------------------
if __name__ == "__main__":
    logging.info("Auto-Ticketing System Started. Monitoring emails...\n")
    try:
        while True:
            mail = connect_to_mailbox()
            if mail:
                check_inbox(mail)
                mail.logout()
            logging.info(f"Waiting {Config.POLL_INTERVAL} seconds before next check...\n")
            countdown(Config.POLL_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Exiting safely. Auto-Ticketing System stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error occurred: {e}")

## press Ctrl+C to stop the script safely ##
