from dataclasses import dataclass

@dataclass(unsafe_hash=True, frozen=True)
class Email:
    to:          str
    subject:     str
    body:        str        
    cc:          str = None # May need to be a list of strings of emails
    attachments: str = None # May need to be a list of strings pointing to path of attachments
    

class Service:
    
    def create_email(self):
        pass

    def discard_email(self):
        pass

    def send_email(self):
        pass

    def display_email(self):
        pass