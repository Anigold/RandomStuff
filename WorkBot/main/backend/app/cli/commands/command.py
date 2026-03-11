from abc import ABC, abstractmethod


class Command(ABC):

    name: str

    def __init__(self, context):
        self.context = context

    @abstractmethod
    def arguments(self):
        pass

    @abstractmethod
    def autocomplete(self, flag: str, text: str):
        pass

    @abstractmethod
    def command(self, args):
        pass

