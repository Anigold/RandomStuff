import Service
import win32com.client
from win32com.client import Dispatch

class OutlookEmail(Service.Email):

    def __init__(self, to: str, subject: str, body: str, cc=None, attachments=None):
        super().__init__(to, subject, body, cc, attachments)


class Outlook(Service):
    
    def create_email(email: OutlookEmail):
        obj = win32com.client.Dispatch("Outlook.Application")
        new_email = obj.CreateItem(0x0)

        new_email.Subject = email.subject
        new_email.To      = email.to
        new_email.Body    = email.body

        if email.cc: new_email.CC = email.cc

        if email.attachments: 
            for attachment in email.attachments: new_email.Attachments.Add(Source=attachment)

        return new_email
    
    def send_email(email: OutlookEmail):
        return email.Send()
    
    def discard_email(email: OutlookEmail):
        return email.Delete()
