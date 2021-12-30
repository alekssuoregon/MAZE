import os
import sys
import json
import logging
sys.path.append(os.path.abspath("../rtt_simulator"))

import constants
import constellation_config
from json import JSONDecodeError
from net_point import NetworkPoint
from collections import defaultdict

"""
config file format: JSON
{
    "SimulationName": String,
    "OutputDirectory": String,
    "SimulationDuration": float(seconds),
    "NetworkPoints": {
        "{Point Name}": {
            "Type": "Terrestrial" | "GroundStation",
            "Location": {
                "Longitude": float,
                "Latitude": float
            }
        },
        ...
    },
    "NetworkOrder": ["{Point Name 1}", ..., "{Point Name N}"],
    "Constellation": Starlink" | "Kuiper" | "Telesat"
}
"""

class SimulationConfig():
    def __init__(self, config_fname):
        self.sim_name = ""
        self.output_dir = ""
        self.duration = 0
        self.constellation = None
        self.network_points = []
        self.__load_config(config_fname)

    def __valid_config(self, config):
        def valid_point(network_point):
            if constants.POINT_TYPE_KEY not in network_point or not isinstance(network_point[constants.POINT_TYPE_KEY], str):
                return False
            if constants.LOCATION_KEY not in network_point or not isinstance(network_point[constants.LOCATION_KEY], dict):
                return False

            if network_point[constants.POINT_TYPE_KEY] not in [constants.CITY_KEY, "GroundStation"]:
                return False

            for key in network_point[constants.LOCATION_KEY].keys():
                if key not in [constants.CITY_KEY, constants.LONGITUDE_KEY, constants.LATITUDE_KEY]:
                    return False
                else:
                    if key == constants.CITY_KEY and not isinstance(network_point[key], str):
                        return False
                    if (key == constants.LONGITUDE_KEY or key == constants.LATITUDE_KEY) and not isinstance(network_point[key], float):
                        return False

            if constants.CITY_KEY not in network_point[constants.LOCATION_KEY]:
                return False
            if network_point[constants.POINT_TYPE_KEY] == "GroundStation":
                if constants.LONGITUDE_KEY not in network_point[constants.LOCATION_KEY] or constants.LATITUDE_KEY not in network_point[constants.LOCATION_KEY]:
                    return False
                else:
                    longitude = network_point[constants.LOCATION_KEY][constants.LONGITUDE_KEY]
                    latitude = network_point[constants.LOCATION_KEY][constants.LATITUDE_KEY]

                    if longitude < -180.0 or longitude > 180.0 or latitude < -90.0 or latitude > 90.0:
                        return False
            return True

        #Validate main config section existence and data types
        valid = constants.SIMULATION_NAME_KEY in config and isinstance(config[constants.SIMULATION_NAME_KEY], str)
        valid = valid and constants.OUTPUT_DIR_KEY in config and isinstance(config[constants.OUTPUT_DIR_KEY], str)
        valid = valid and constants.DURATION_KEY in config and isinstance(config[constants.DURATION_KEY], float) and \
                config[constants.DURATION_KEY] > 0
        valid = valid and constants.NETWORK_POINTS_KEY in config and isinstance(config[constants.NETWORK_POINTS_KEY], dict)
        valid = valid and constants.NETWORK_ORDER_KEY in config and isinstance(config[constants.NETWORK_ORDER_KEY], list) and \
                len(config[constants.NETWORK_ORDER_KEY]) == len(set(config[constants.NETWORK_ORDER_KEY]))
        valid = valid and constants.CONSTELLATION_KEY in config and isinstance(config[constants.CONSTELLATION_KEY], str) and \
                config[constants.CONSTELLATION_KEY] in ["Starlink", "Kuiper", "Telesat"]

        if not valid:
            return False

        #Validate network point entries
        #Check if network point order is valid(AKA gs-to-gs or terra-to-gs pairs)
        network_points = config[constants.NETWORK_POINTS_KEY]
        point_names = set(list(network_points.keys()))
        for point_name in point_names:
            cur_point = network_points[point_name]
            if not isinstance(cur_point, dict) or not valid_point(cur_point):
                return False

        network_order = config[constants.NETWORK_ORDER_KEY]
        for point_name in network_order:
            if point_name not in point_names:
                return False

        prev_prev_point = None
        prev_point = network_order[0]
        for i in range(1, len(network_order))
            point_name = network_order[i]
            if prev_point[constants.POINT_TYPE_KEY] == constants.GS_POINT_TYPE:
                if prev_prev_point is None or prev_prev_point[constants.POINT_TYPE_KEY] != constants.GS_POINT_TYPE:
                    if network_points[point_name][constants.POINT_TYPE_KEY] != constants.GS_POINT_TYPE:
                        return False
            elif network_points[point_name][constants.POINT_TYPE_KEY] == constants.GS_POINT_TYPE and point_name == network_order[-1]:
                return False

            prev_prev_point = prev_point
            prev_point = network_points[point_name]

        return True

    def __load_config(self, fname):
        if not os.path.isfile(fname):
            raise ValueError("Invalid config filename: '" + fname + "' does not exist")

        config = None
        with open(fname, "r") as fp:
            #handle error throw
            try:
                config = json.load(fp)
            except JSONDecodeError as e:
                logging.error("Failed to load JSON file '" + fname + "': " + str(e))
                raise ValueError("Bad config file: Invalid JSON")


        if not self.__valid_config(config):
            raise ValueError("Bad config file: Invalid format")

        self.sim_name = config[constants.SIMULATION_NAME_KEY]
        self.output_dir = config[constants.OUTPUT_DIR_KEY]
        self.duration = int(config[constants.DURATION_KEY])

        for point_name in config[constants.NETWORK_ORDER_KEY]:
            point_def = config[constants.NETWORK_POINTS_KEY][point_name]
            type = point_def[constants.POINT_TYPE_KEY]
            city = point_def[constants.LOCATION_KEY][constants.CITY_KEY]

            latitude = point_def[constants.LOCATION_KEY][constants.LATITUDE_KEY]
            longitude = point_def[constants.LOCATION_KEY][constants.LONGITUDE_KEY]
            network_point = NetworkPoint(point_name, type, city, latitude, longitude)

            self.network_points.append(network_point)

        if config[constants.CONSTELLATION_KEY] == "Starlink":
            self.constellation = constellation_config.GetStarlinkConfig()
        elif config[constants.CONSTELLATION_KEY] == "Kuiper":
            self.constellation = constellation_config.GetKuiperConfig()
        else:
            self.constellation = constellation_config.GetTelesatConfig()

    def duration(self):
        return self.duration
        
    def network_points(self):
        for point in self.network_points:
            yield point

    def constellation():
        return self.constellation
