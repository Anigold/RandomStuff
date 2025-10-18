from typing import Callable, Dict
from backend.adapters.emailer.services.service import EmailService

class EmailProviderRegistry:
    _providers: Dict[str, Callable[[], EmailService]] = {}

    @classmethod
    def register(cls, name: str, factory: Callable[[], EmailService]):
        cls._providers[name.lower()] = factory

    @classmethod
    def get(cls, name: str) -> EmailService:
        if name.lower() not in cls._providers:
            raise ValueError(f"No email provider registered for '{name}'")
        return cls._providers[name.lower()]()
