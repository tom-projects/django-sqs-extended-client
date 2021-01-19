from abc import ABC, abstractmethod


class EventBase(ABC):

    @abstractmethod
    def dispatch(self, event_name, event_data):
        pass