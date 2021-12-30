import math
from network_simulator import NetworkSimulator

class DistanceBasedPingCalculator():
    def __init__(self, distance_km, rtt_ms):
        self.__distance_km = distance_km
        self.__rtt_ms = rtt_ms

    @staticmethod
    def __crow_flies_distance(lat1, long1, lat2, long2):
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
        segment_distance = DistanceBasedPingCalculator.__crow_flies_distance( \
            lat1, long1, lat2, long2)
        distance_percent = segment_distance / self.__distance_km

        calculated_rtt = distance_percent * self.__rtt_ms
        return calculated_rtt


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
