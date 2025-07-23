from .services.service import Service, Email
from .services.gmail_service import GmailService
from pprint import pprint

class Emailer:

    def __init__(self, service: Service) -> None:
        self.service = service 
        self.emails = {}
        '''
        {
            Email_Object: email_instance
        }
        '''

    def create_email(self, email: Email) -> None:
        self.emails[email] = self.service.create_email(email)

    
    def send_email(self, email: Email) -> None:
        return self.service.send_email(self.emails[email]) if email in self.emails else None

    # def discard_email(self, email: Email) -> None:
    #     for saved_email in self.emails:
    #         if email == saved_email:
    #             self.service.delete_email(self.emails.pop(self.emails.index(saved_email)))
    #     return
    
    def get_email(self, email: Email) -> dict:
        return {email: self.emails[email]} if email in self.emails else None
        
    def display_email(self, email: Email) -> None:
        return self.service.display_email(email) if email in self.emails else None