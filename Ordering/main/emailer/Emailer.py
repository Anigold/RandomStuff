from .Services import Outlook

class Emailer:

    def __init__(self, service: Service) -> None:
        self.service = service