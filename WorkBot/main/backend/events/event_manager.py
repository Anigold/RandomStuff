import json
from .google_calendar_api import GoogleCalendarAPI

class EventManager:
    def __init__(self, creds_path, calendar_id, recipients_path):
        self.calendar = GoogleCalendarAPI(creds_path, calendar_id)
        with open(recipients_path, 'r') as f:
            self.recipients = json.load(f)

    def categorize_event(self, event):
        for category in self.recipients:
            if category.lower() in event['summary'].lower():
                return category
        return None

    def get_categorized_events(self):
        events = self.calendar.get_upcoming_events()
        categorized = []

        for event in events:
            category = self.categorize_event(event)
            if category:
                categorized.append((category, event))

        return categorized
