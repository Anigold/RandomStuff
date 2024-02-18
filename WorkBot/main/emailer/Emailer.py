from .Services.Service import Service, Email

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
        if email not in self.emails:
            self.emails[email] = self.service.create_email(email)
        else:
            self.emails[email].update(self.service.create_email(email)) 
        return
    
    def send_email(self, email: Email) -> None:
        return self.service.send_email(self.emails[email]) if email in self.emails else None

    # def discard_email(self, email: Email) -> None:
    #     for saved_email in self.emails:
    #         if email == saved_email:
    #             self.service.delete_email(self.emails.pop(self.emails.index(saved_email)))
    #     return
    
    def get_email(self, email: Email) -> dict:
        if email in self.emails:
            return {email: self.emails[email]}