from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

# Gmail API scopes: now includes both read + send
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def main():
    creds = None
    creds_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'credentials.json')

    if not os.path.exists(creds_path):
        print(f"❌ credentials.json not found at: {creds_path}")
        return

    if os.path.exists('token.json'):
        print("Token already exists. Delete it to re-authenticate if needed.")
    else:
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("✅ Authentication complete! Token saved as token.json.")

if __name__ == '__main__':
    main()
