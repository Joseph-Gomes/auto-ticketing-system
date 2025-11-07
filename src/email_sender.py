import os
import base64
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def send_auto_reply(to_email, subject, ticket_id):
    """
    Sends an auto-reply email using Gmail API, SendGrid, or SMTP (fallback).
    Priority: Gmail API → SendGrid → SMTP.
    """
    logging.info(f"Attempting to send auto-reply to {to_email} (Ticket ID: {ticket_id})")

    # Email body (HTML)
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Dear Customer,</p>
        <p>We’ve received your support request regarding: <b>{subject}</b>.</p>
        <p>Your Ticket ID is: <b style="color:#0078D7;">{ticket_id}</b>.</p>
        <p>Our support team will review your ticket and get back to you shortly.</p>
        <br>
        <p>Thank you for contacting <b>IT Support</b>.</p>
        <p>Kind regards,<br>
        <b>Auto-Ticketing System</b><br>
        IT Support Team<br>
        <a href="mailto:{Config.EMAIL}">{Config.EMAIL}</a></p>
        <hr>
        <small style="color:#888;">This is an automated message. Please do not reply directly.</small>
    </body>
    </html>
    """

    # ========================================
    # 1️⃣ Try Gmail API (if token.json exists)
    # ========================================
    try:
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            service = build("gmail", "v1", credentials=creds)

            message = MIMEText(html_content, "html")
            message["to"] = to_email
            message["subject"] = f"[Ticket Received] {subject} (ID: {ticket_id})"

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            service.users().messages().send(userId="me", body={"raw": raw_message}).execute()

            logging.info(f"✅ Auto-reply sent successfully via Gmail API to {to_email}")
            return True
        else:
            logging.warning("⚠️ token.json not found. Trying SendGrid next...")
    except Exception as e:
        logging.error(f"❌ Gmail API failed ({e}). Trying SendGrid...")

    # ========================================
    # 2️⃣ Try SendGrid API
    # ========================================
    try:
        sendgrid_api = os.getenv("SENDGRID_API_KEY")
        if sendgrid_api:
            message = Mail(
                from_email=Config.EMAIL,
                to_emails=to_email,
                subject=f"[Ticket Received] {subject} (ID: {ticket_id})",
                html_content=html_content,
            )
            sg = SendGridAPIClient(sendgrid_api)
            response = sg.send(message)

            if response.status_code in (200, 202):
                logging.info(f"✅ Auto-reply sent successfully via SendGrid to {to_email}")
                return True
            else:
                logging.error(f"❌ SendGrid returned status {response.status_code}: {response.body}")
        else:
            logging.warning("⚠️ SENDGRID_API_KEY not found in environment. Using SMTP fallback...")
    except Exception as e:
        logging.error(f"❌ SendGrid failed ({e}). Trying SMTP fallback...")

    # ========================================
    # 3️⃣ Final Fallback — Gmail SMTP
    # ========================================
    try:
        sender_email = Config.EMAIL
        sender_pass = Config.EMAIL_PASSWORD

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Ticket Received] {subject} (ID: {ticket_id})"
        msg["From"] = sender_email
        msg["To"] = to_email
        msg.attach(MIMEText(html_content, "html"))

        logging.info("🔐 Connecting to Gmail SMTP...")
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_pass)
            server.send_message(msg)

        logging.info(f"✅ Auto-reply sent successfully via SMTP to {to_email}")
        return True
    except Exception as e:
        logging.error(f"❌ SMTP general error: {e}")
        return False
