from dataclasses import dataclass

@dataclass(unsafe_hash=True, frozen=True)
class Email:
    to:          str
    subject:     str
    body:        str        
    cc:          str = None
    attachments: str = None # May need to be a list of strings pointing to path of attachments
    

class Service:
    
    def create_email():
        pass

    def discard_email():
        pass

    def send_email():
        pass