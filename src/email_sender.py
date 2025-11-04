import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import logging

# Gmail API scopes for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_auto_reply(to_email, subject, ticket_id):
    """
    Sends a professional auto-reply email confirming receipt of a support ticket.
    """
    logging.info(f"Attempting to send auto-reply to {to_email} (Ticket ID: {ticket_id})")

    try:
        # Load credentials
        if not os.path.exists('token.json'):
            logging.error("token.json not found. Run Gmail auth first (gmail_auth_test.py).")
            return False

        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # Create Gmail service
        service = build('gmail', 'v1', credentials=creds)

        # Email content (HTML)
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
            <a href="mailto:autoticketingproject@gmail.com">autoticketingproject@gmail.com</a></p>
            <hr>
            <small style="color: #888;">This is an automated message. Please do not reply directly to this email.</small>
        </body>
        </html>
        """

        message = MIMEText(html_content, 'html')
        message['to'] = to_email
        message['subject'] = f"[Ticket Received] {subject} (ID: {ticket_id})"

        # Encode message and send
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body = {'raw': raw_message}

        send_message = service.users().messages().send(userId='me', body=body).execute()

        logging.info(f"Auto-reply sent successfully to {to_email} (Ticket ID: {ticket_id})")
        return True

    except Exception as e:
        logging.error(f"Failed to send auto-reply to {to_email}: {e}")
        return False
