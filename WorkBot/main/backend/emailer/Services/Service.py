from dataclasses import dataclass

@dataclass(unsafe_hash=True, frozen=True)
class Email:
    to:          tuple
    subject:     str
    body:        str        
    cc:          tuple = None # We use a tuple to remain hashable
    attachments: tuple = None # We use a tuple to remain hashable
    

class Service:
    
    def create_email(self):
        pass

    def discard_email(self):
        pass

    def send_email(self):
        pass

    def display_email(self):
        pass