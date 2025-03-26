from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

class GoogleCalendarAPI:
    def __init__(self, creds_path, calendar_id):
        self.creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        self.service = build('calendar', 'v3', credentials=self.creds)
        self.calendar_id = calendar_id

    def get_upcoming_events(self, days_ahead=7):
        now = datetime.utcnow().isoformat() + 'Z'
        max_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'

        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=now,
            timeMax=max_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])
