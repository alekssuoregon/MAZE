import math
from network_simulator import NetworkSimulator

class DistanceBasedPingCalculator():
    def __init__(self, distance_km, rtt_ms):
        self._distance_km = distance_km
        self._rtt_ms = rtt_ms

    @staticmethod
    def _crow_flies_distance(lat1, long1, lat2, long2):
        to_rad_conv = 57.29577951
        rad_lat1 = lat1 / to_rad_conv
        rad_long1 = long1 / to_rad_conv
        rad_lat2 = lat2 / to_rad_conv
        rad_long2 = long2 / to_rad_conv

        d = 3963.0 * math.acos((math.sin(rad_lat1) * math.sin(rad_lat2)) + \
            math.cos(rad_lat1) * math.cos(rad_lat2) * math.cos(rad_long2 - rad_long1))
        d *= 1.609344
        return d

    def rtt_between(self, lat1, long1, lat2, long2):
        segment_distance = DistanceBasedPingCalculator._crow_flies_distance( \
            lat1, long1, lat2, long2)
        distance_percent = segment_distance / self._distance_km

        calculated_rtt = distance_percent * self._rtt_ms
        return calculated_rtt
