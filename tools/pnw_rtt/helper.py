import os
import sys
import logging
from abc import ABC, abstractmethod
sys.path.append(os.path.abspath("../../rtt_simulator"))
sys.path.append(os.path.abspath(".."))

import constants
import sim_config
import net_segment
from network_simulator import NetworkSimulator
from sat_relay_sim import GroundstationMap, SatelliteNetworkState, SatelliteRelaySimulator
from terrestrial_simulator import DistanceBasedPingCalculator

class PNWDistanceBasedRTTSimulator(NetworkSimulator, DistanceBasedPingCalculator):
    _seattle_to_la_km = DistanceBasedPingCalculator._crow_flies_distance(47.6062, -122.3321, 34.0522, -118.2437)
    _seattle_to_la_rtt_ms = 32.986

    def __init__(self, datapoints_per):
        NetworkSimulator.__init__(self)
        DistanceBasedPingCalculator.__init__(self, PNWDistanceBasedRTTSimulator._seattle_to_la_km, PNWDistanceBasedRTTSimulator._seattle_to_la_rtt_ms, 5.0)
        self._datapoints_per_run = datapoints_per

    def generate_rtts(self, src, dst):
        lat1, long1 = src.location()
        lat2, long2 = dst.location()

        calculated_rtt = self.rtt_between(lat1, long1, lat2, long2)
        return (calculated_rtt for i in range(self._datapoints_per_run))

class PNWMixedNetworkRTTSimulator(NetworkSimulator):
    def __init__(self, config, project_dir, gs_map):
        self._config = config
        self._project_dir = project_dir
        self._network_segments = None
        self._datapoints_per_run = 0
        self._groundstation_map = gs_map
        self._network_segments = []

        self._datapoints_per_run = int((self._config.duration() * 1000) / constants.TIMESTEP_MS)
        terra_simulator = PNWDistanceBasedRTTSimulator(self._datapoints_per_run)

        state_dir = self._project_dir + "/" + self._config.constellation().name
        exterra_simulator = SatelliteRelaySimulator(self._groundstation_map, self._config.duration(), state_dir, self._project_dir, os.path.abspath("../../satgenpy"))
        net_segment.NetworkSegment.configure(exterra_simulator, terra_simulator)
        self._populate_network_segments()

    @abstractmethod
    def _populate_network_segments(self):
        pass

    @abstractmethod
    def get_param_order(self):
        pass


class PNWMixedNetworkPathRTTSimulator(PNWMixedNetworkRTTSimulator):
    def __init__(self, config, project_dir, gs_map):
        super().__init__(config, project_dir, gs_map)

    def _populate_network_segments(self):
        self._network_segments = []

        cur_point = None
        past_point = None

        for network_point in self._config.network_points():
            past_point = cur_point
            cur_point = network_point
            if past_point is not None:
                new_seg = net_segment.NetworkSegment(past_point, cur_point)
                self._network_segments.append(new_seg.get_rtts())

    def get_param_order(self):
        return tuple(["path"])

    def generate_rtts(self):
        for i in range(self._datapoints_per_run):
            total_rtt = 0.0
            for segment in self._network_segments:
                total_rtt += next(segment)
            yield tuple([total_rtt])

class PNWMixedNetworkEveryPairRTTSimulator(PNWMixedNetworkRTTSimulator):
    def __init__(self, config, project_dir, gs_map):
        super().__init__(config, project_dir, gs_map)

    def _populate_network_segments(self):
        self._network_segments = []
        self._segment_header = []
        seen = set()
        for network_point_a in self._config.network_points():
            for network_point_b in self._config.network_points():
                header = "/".join(sorted([network_point_a.name(), network_point_b.name()]))
                if network_point_a != network_point_b and header not in seen:
                    new_seg = net_segment.NetworkSegment(network_point_a, network_point_b)
                    self._network_segments.append(new_seg.get_rtts())
                    self._segment_header.append(header)
                    seen.add(header)

    def get_param_order(self):
        return tuple(self._segment_header)

    def generate_rtts(self):
        for i in range(self._datapoints_per_run):
            rtts = [0 for _ in range(len(self._network_segments))]
            for i in range(len(self._network_segments)):
                rtts[i] = next(self._network_segments[i])
            yield tuple(rtts)


def generate_network_state(config, output_dir):
    constellation = config.constellation()
    state_dir = output_dir + "/" + constellation.name
    logging.info("Generating satellite constellation state...")
    state_generator = SatelliteNetworkState(constellation, config.all_points(), config.duration(), output_dir)
    state_generator.create()
    gs_map = state_generator.groundstation_map(save_to_fname=state_dir+"/g_map.txt")
    gs_map.save()

def retrieve_network_state(config, output_dir):
    gs_map = None
    constellation = config.constellation()
    state_dir = output_dir + "/" + constellation.name

    logging.info("Loading satellite constellation metadata...")
    g_map_fname = state_dir + "/g_map.txt"
    if not os.path.exists(g_map_fname):
        raise ValueError("Failed to load metadata. No satellite metadata found at " + g_map_fname)
    if not os.access(g_map_fname, os.R_OK):
        raise ValueError("Failed to load metadata. Invalid permissions to read file " + g_map_fname)

    gs_map = GroundstationMap(state_dir + "/g_map.txt")
    gs_map.load()
    return gs_map
