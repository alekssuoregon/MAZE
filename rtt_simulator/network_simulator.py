from abc import ABC, abstractmethod

class NetworkSimulator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def generate_rtts(self, src, dst):
        pass
