from abc import ABC, abstractmethod

class NetworkSimulator(ABC):
    """
    NetworkSimulator is an interface describing a class which can generate
    Round Trip Times between two points
    """
    def __init__(self):
        pass

    @abstractmethod
    def generate_rtts(self, src, dst):
        """
        generate_rtts creates and returns a generator object yielding all
        calculated Round Trip Times between two nodes

        :param net_point.NetworkPoint src: Start node
        :param net_point.NetworkPoint dst: End node
        :return: Generator object
        """
        pass
