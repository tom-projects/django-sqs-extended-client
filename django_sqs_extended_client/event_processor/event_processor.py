from abc import ABC, abstractmethod


class EventProcessor(ABC):

    def __init__(self, **kwargs):
        self.data = kwargs.get('data')
        self.attributes = kwargs.get('attributes', {})
        self.queue_code = kwargs.get('queue_code')

    @abstractmethod
    def execute(self):
        pass