import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import smtplib
from config import Config
import os
import logging

# Gmail API scopes for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def send_auto_reply(to_email, subject, ticket_id):
    """
    Sends a professional auto-reply email confirming receipt of a support ticket.
    Tries Gmail API first; falls back to SMTP if token.json not found or invalid.
    """
    logging.info(f"Attempting to send auto-reply to {to_email} (Ticket ID: {ticket_id})")

    # --- Shared HTML email content ---
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Dear Customer,</p>
        <p>We’ve received your support request regarding: <b>{subject}</b>.</p>
        <p>Your Ticket ID is: <b style="color:#0078D7;">{ticket_id}</b>.</p>
        <p>Our support team will review your ticket and get back to you shortly.</p>
        <br>
        <p>Thank you for contacting <b>IT Support</b>.</p>
        <p>Kind regards, <br>
        <b>Auto-Ticketing System</b><br>
        IT Support Team<br>
        <a href="mailto:{Config.EMAIL}">{Config.EMAIL}</a></p>
        <hr>
        <small style="color: #888;">This is an automated message. Please do not reply directly to this email.</small>
    </body>
    </html>
    """

    # =========================
    # 🧩 Try Gmail API first
    # =========================
    try:
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            service = build("gmail", "v1", credentials=creds)

            message = MIMEText(html_content, "html")
            message["to"] = to_email
            message["subject"] = f"[Ticket Received] {subject} (ID: {ticket_id})"

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            body = {"raw": raw_message}

            service.users().messages().send(userId="me", body=body).execute()

            logging.info(f"✅ Auto-reply sent successfully via Gmail API to {to_email} (Ticket ID: {ticket_id})")
            return True
        else:
            logging.warning("⚠️ token.json not found. Falling back to SMTP method...")

    except Exception as e:
        logging.error(f"❌ Gmail API failed ({type(e).__name__}: {e}). Falling back to SMTP method...")

    # =========================
    # 💌 Fallback: Use SMTP
    # =========================
    try:
        sender_email = Config.EMAIL
        sender_pass = Config.EMAIL_PASSWORD

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Ticket Received] {subject} (ID: {ticket_id})"
        msg["From"] = sender_email
        msg["To"] = to_email

        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_pass)
            server.send_message(msg)

        logging.info(f"✅ Auto-reply sent successfully via SMTP to {to_email} (Ticket ID: {ticket_id})")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"❌ SMTP Auth Error: {e.smtp_error.decode() if hasattr(e, 'smtp_error') else e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logging.error(f"❌ SMTP Recipients Refused: {e.recipients}")
        return False
    except Exception as e:
        logging.error(f"❌ Failed to send auto-reply via SMTP: {type(e).__name__}: {e}")
        return False
