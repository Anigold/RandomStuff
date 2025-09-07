import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from .service import Service, Email
from config.paths import CREDENTIALS_DIR

GOOGLE_API_CREDS_DIR = CREDENTIALS_DIR / 'GoogleAPI'

class GmailService(Service):

    def __init__(self, credentials_path=GOOGLE_API_CREDS_DIR / 'creds.json', token_path=GOOGLE_API_CREDS_DIR / 'token.pickle'):

        self.SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        self.creds  = None

        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('gmail', 'v1', credentials=self.creds)

    def create_email(self, email: Email) -> dict:

        if not email.to or not all(email.to):
            raise ValueError('Email must have at least one valid "to" address.')

        msg = MIMEMultipart()
        msg['To'] = ', '.join(addr.strip().rstrip(',') for addr in email.to)
        msg['Subject'] = email.subject

        if email.cc and all(email.cc):
            msg['Cc'] = msg['Cc'] = ', '.join(addr.strip().rstrip(',') for addr in email.cc)

        msg.attach(MIMEText(email.body, 'plain'))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        return {
            'raw': raw,
            'to': email.to,
        }


    def send_email(self, email_data: dict) -> None:
        self.service.users().messages().send(userId='me', body={'raw': email_data['raw']}).execute()

    def display_email(self, email_data: dict) -> None:
        print('Base64 Encoded Message:')
        print(email_data['to'])
        print(email_data['raw'])
