import constants

class NetworkSegment():
    """
    NetworkSegment describes a connection between two nodes on the network
    path

    :param net_point.NetworkPoint net_point_a: The start node in the segment
    :param net_point.NetworkPoint net_point_b: The end node in the segment
    """
    _extraterra_sim = None
    _terra_sim = None
    _is_configured = False

    @classmethod
    def configure(cls, et_sim, terra_sim):
        """
        configure configures the NetworkSegment class with the required simulators
        to allow the calculation of the segments Round Trip Time

        :param network_simulator.NetworkSimulator et_sim: The simulator for calculating
            RTTs between two ground station nodes via satellite constellation
        :param network_simulator.NetworkSimulator terra_sim: The simulator for calculating
            RTTs between two nodes, one of which is not a ground station node
        """
        cls._extraterra_sim = et_sim
        cls._terra_sim = terra_sim
        cls._is_configured = True

    def __init__(self, net_point_a, net_point_b):
        self._point_a = net_point_a
        self._point_b = net_point_b
        self._rtts = None

    def _run_rtt_simulation(self):
        simulator = self._extraterra_sim
        if self._point_a.type() != constants.GS_POINT_TYPE or \
            self._point_b.type() != constants.GS_POINT_TYPE:
            simulator = self._terra_sim

        self._rtts = [rtt for rtt in simulator.generate_rtts(self._point_a, self._point_b)]

    def get_rtts(self):
        """
        get_rtts returns a generator which yields each individual calculated
            RTT in milliseconds of the segment

        :return: Generator object
        """
        if self._rtts is None:
            self._run_rtt_simulation()
        return (rtt for rtt in self._rtts)

    def avg_rtt(self):
        """
        avg_rtt returns the mean RTT in milliseconds of the segment

        :return: float
        """
        if self._rtts is None:
            self._run_rtt_simulation()
        return sum(self._rtts) / float(len(self._rtts))
