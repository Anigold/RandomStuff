from backend.emailer.Emailer import Emailer
from .event_manager import EventManager

class EventEmailer:
    def __init__(self, creds_path, calendar_id, recipients_path):
        self.event_manager = EventManager(creds_path, calendar_id, recipients_path)
        self.emailer = Emailer()

    def send_event_notifications(self):
        events = self.event_manager.get_categorized_events()
        for category, event in events:
            recipients = self.event_manager.recipients[category]
            subject = f"[{category}] Upcoming Event: {event['summary']}"
            body = f"📅 {event['start']['dateTime']}\n\n{event.get('description', 'No description')}"
            self.emailer.send_email(recipients, subject, body)
