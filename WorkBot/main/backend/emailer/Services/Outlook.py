from .Service import Service, Email

try:
    import win32com.client
    from win32com.client import Dispatch
except:
    pass


from dataclasses import dataclass


class OutlookService(Service):
    
    def create_email(self, email: Email):
     
        obj = win32com.client.Dispatch("Outlook.Application")
        new_email = obj.CreateItem(0x0)

        new_email.Subject = email.subject
        new_email.To      = ';'.join(email.to)
        new_email.Body    = email.body

        if email.cc: new_email.CC = email.cc

        if email.attachments: 
            for attachment in email.attachments: new_email.Attachments.Add(Source=str(attachment))

        return new_email
    
    def send_email(self, email: Email):
        return email.Send()
    
    def discard_email(self, email: Email):
        return email.Delete()

    def display_email(self, email: Email):
        email_to_display = self.create_email(email)
        return email_to_display.display()
    
    def get_inbox(self):
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        return outlook.GetDefaultFolder(6)  # 6 = Inbox
    
    def refresh_inbox(self):
        """
        Nudges Outlook to refresh the Inbox by accessing the last item.
        """
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6)  # Inbox

        # Force a send/receive for all accounts
        namespace.SendAndReceive(False)

    def get_recent_messages(self, subject_filter=None, sender_filter=None, max_age_minutes=10):
        from datetime import datetime, timedelta, timezone
        MAIL_ITEM = 43
        inbox = self.get_inbox()
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)

        # time_limit = datetime.now() - timedelta(minutes=max_age_minutes)
        time_limit = datetime.now(timezone.utc) - timedelta(minutes=max_age_minutes)
        for msg in messages:
            try:
                if msg.Class != MAIL_ITEM:
                    continue
                if msg.ReceivedTime < time_limit:
                    print('Bad time')
                    continue
                if subject_filter and subject_filter.lower() not in msg.Subject.lower():
                    continue
                if sender_filter and sender_filter.lower() not in msg.SenderEmailAddress.lower():
                    continue
                yield msg
            except Exception as e:
                print(f'Something went wrong: {e}', flush=True)
                continue