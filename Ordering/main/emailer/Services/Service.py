from dataclasses import dataclass

@dataclass(unsafe_hash=True)
class Email:
    to:          str
    subject:     str
    body:        str        
    cc:          str = None
    attachments: str = None
    

class Service:
    
    def create_email():
        pass

    def discard_email():
        pass

