from .Service import Service, Email

try:
    import win32com.client
    from win32com.client import Dispatch
except:
    pass


from dataclasses import dataclass


class Outlook(Service):
    
    def create_email(self, email: Email):
     
        obj = win32com.client.Dispatch("Outlook.Application")
        new_email = obj.CreateItem(0x0)

        new_email.Subject = email.subject
        new_email.To      = ';'.join(email.to)
        new_email.Body    = email.body

        if email.cc: new_email.CC = email.cc

        if email.attachments: 
            for attachment in email.attachments: new_email.Attachments.Add(Source=attachment)

        return new_email
    
    def send_email(self, email: Email):
        return email.Send()
    
    def discard_email(self, email: Email):
        return email.Delete()

    def display_email(self, email: Email):
        email_to_display = self.create_email(email)
        return email_to_display.display()