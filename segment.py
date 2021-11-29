from abc import ABC, abstractmethod

class NetworkSegment(ABC):
    def __init__(self, point_a, point_b):
        self.point_a = point_a
        self.point_b = point_b

    @abstractmethod
    def calculate_rtt(self):
        pass

class SatelliteSegment(NetworkSegment):
    def __init__(self, sat_sim, point_a, point_b):
        super().__init__(point_a, point_b)
        self.simulator = sat_sim
