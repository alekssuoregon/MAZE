import constants

class NetworkSegment():
    _extraterra_sim = None
    _terra_sim = None
    _is_configured = False

    @classmethod
    def configure(cls, et_sim, terra_sim):
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
        if self._rtts is None:
            self._run_rtt_simulation()
        return (rtt for rtt in self._rtts)

    def avg_rtt(self):
        if self._rtts is None:
            self._run_rtt_simulation()
        return sum(self._rtts) / float(len(self._rtts))
