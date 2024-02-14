class Email:
    def __init__(self, to: str, subject: str, body: str, cc=None, attachments=None):
        self.to          = to
        self.subject     = subject
        self.body        = body
        self.cc          = cc
        self.attachments = attachments

class Service:
    
    def create_email():
        pass

    def discard_email():
        pass

