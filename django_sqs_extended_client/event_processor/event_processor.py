from abc import ABC, abstractmethod


class EventProcessor(ABC):

    def __init__(self, data, attributes, queue_code):
        self.data = data
        self.attributes = attributes
        self.queue_code = queue_code

    @abstractmethod
    def execute(self):
        pass