import math
import random
from network_simulator import NetworkSimulator

class DistanceBasedPingCalculator():
    """
    DistanceBasedPingCalculator estimates the Round Trip Time between two
    points based on the known Round Trip Time and distance between two
    master points

    :param float distance_km: Distance between the two master points in kilometers
    :param float rtt_ms: Round Trip Time between the two master points
    """
    def __init__(self, distance_km, rtt_ms, jitter_ms):
        self._distance_km = distance_km
        self._rtt_ms = rtt_ms
        self._jitter_ms = jitter_ms

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
        """
        rtt_between estimates the Round Trip Time between geographical points

        :param float lat1: Latitude of point one
        :param float long1: Longitude of point one
        :param float lat2: Latitude of point two
        :param float long2: Longitude of point two
        :return: Estimated Round Trip Time in milliseconds
        """
        segment_distance = DistanceBasedPingCalculator._crow_flies_distance( \
            lat1, long1, lat2, long2)
        distance_percent = segment_distance / self._distance_km

        calculated_rtt = distance_percent * self._rtt_ms
        calculated_rtt += float(random.randrange(0, self._jitter_ms * 100)) / 100.0
        return calculated_rtt
