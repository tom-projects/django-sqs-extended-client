from abc import ABC, abstractmethod


class EventProcessor(ABC):

    def __init__(self, data):
        self.data = data

    @abstractmethod
    def execute(self):
        pass