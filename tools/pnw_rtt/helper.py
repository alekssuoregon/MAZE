import os
import sys
sys.path.append(os.path.abspath("../../rtt_simulator"))
sys.path.append(os.path.abspath(".."))

import sim_config
import net_segment
from network_simulator import NetworkSimulator
from sat_relay_sim import GroundstationMap, SatelliteRelaySimulator
from terrestrial_simulator import DistanceBasedPingCalculator

class PNWDistanceBasedRTTSimulator(NetworkSimulator, DistanceBasedPingCalculator):
    __seattle_to_la_km = DistanceBasedPingCalculator.__crow_flies_distance(47.6062, 122.3321, 34.0522, 118.2437)
    __seattle_to_la_rtt_ms = 32.986

    def __init__(self, datapoints_per):
        TerrestrialRTTSimulator.__init__(self)
        DistanceBasedPingCalculator.__init__(self, __seattle_to_la_km, __seattle_to_la_rtt_ms)
        self._datapoints_per_run = datapoints_per

    def generate_rtts(self, src, dst):
        lat1, long1 = src.location()
        lat2, long2 = dst.location()

        calculated_rtt = self.rtt_between(lat1, long1, lat2, long2)
        return (calculated_rtt for i in range(self._datapoints_per_run))

class PNWMixedNetworkRTTSimulator():
    def __init__(self, config, gs_map):
        self._config = config
        self._network_segments = None
        self._datapoints_per_run = 0
        self._groundstation_map = gs_map

    def _create_sim_resources(self):
        self._datapoint_per_run = (self._config.duration() * 1000) / constants.TIMESTEP_MS
        terra_simulator = PNWDistanceBasedRTTSimulator(self._datapoints_per_run)
        exterra_simulator = SatelliteRelaySimulator(gs_map, self._config.duration(), )
        net_segment.NetworkSegment.configure(terra_simulator, exterra_simulator)
        self._network_segments = []

        cur_point = None
        past_point = None

        for network_point in config.network_points():
            past_point = cur_point
            cur_point = network_point
            if past_point is not None:
                new_seg = net_segment.NetworkSegment(past_point, cur_point)
                self._network_segments.append(new_seg.get_rtts())

    def generate_rtts(self):
        for i in range(self._datapoint_per_run):
            total_rtt = 0.0
            for segment in self._network_segments:
                total_rtt += next(segment)
            total_rtt /= len(self._network_segments)
            yield total_rtt

def retrieve_network_state(config, state_path, gen_state=False):
    gs_map = None

    if gen_state:
        state_generator = SatelliteNetworkState(config.constellation(), config.network_points(), config.duration(), state_path)
        state_generator.create()
        gs_map = state_generator.groundstation_map(save_to_fname=state_path + "/g_map.txt")
        gs_map.save()
    else:
        gs_map = GroundstationMap(state_path + "/g_map.txt")
        gs_map.load()
    return gs_map
