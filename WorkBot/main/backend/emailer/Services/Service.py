from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional, Tuple

@dataclass(unsafe_hash=True, frozen=True)
class Email:
    to:          Tuple[str, ...]
    subject:     str
    body:        str        
    cc:          Optional[Tuple[str, ...]] = None # We use a tuple to remain hashable
    attachments: Optional[Tuple[str, ...]] = None # We use a tuple to remain hashable
    

class Service(ABC):
    
    @abstractmethod
    def create_email(self, email: Email) -> dict:
        pass

    @abstractmethod
    def send_email(self, email_data: dict) -> None:
        pass

    @abstractmethod
    def display_email(self, email_data: dict) -> None:
        pass