import csv
import argparse
import os
from collections import defaultdict

class RTTSectorPointMap():
    def __init__(self):
        self._map = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))

    def _find_key_order(self, a, b):
        left = a
        right = b
        if a[0] < b[0]:
            left, right = right, left
        return (left, right)

    def put(self, source, dest, rtt):
        left, right = self._find_key_order(source, dest)
        self._map[left[0]][left[1]][right[0]][right[1]] = rtt

    def get(self, source, dest):
        left, right = self._find_key_order(source, dest)
        return self._map[left[0]][left[1]][right[0]][right[1]]


def read_rtt_data(fp):
    """
    :param fp: File pointer
    :return: (Dictionary mapping Sectors->points and Dictionary RTTSectorPointMap object)
    """
    header = fp.readline().strip().split(",")[1:]
    rtts = [0.0 for _ in range(len(header))]

    total_entries = 0
    for line in fp:
        entry = line.strip().split(",")
        total_entries += 1

        for i in range(1, len(entry)):
            rtts[i-1] += float(entry[i])

    for i in range(len(rtts)):
        rtts[i] /= total_entries

    rtt_map = RTTSectorPointMap()
    sector_point_map = defaultdict(lambda: set())
    for i in range(len(header)):
        source, dest = header[i].split("/")
        source_point = tuple(source.split("_"))
        dest_point = tuple(dest.split("_"))

        sector_point_map[source_point[0]].add(source_point[1])
        sector_point_map[dest_point[0]].add(dest_point[1])
        rtt_map.put(source_point, dest_point, rtts[i])

    return (sector_point_map, rtt_map)


def find_optimal_configuration(sector_list, rtt_mapping):
    """
    :param configuration: Set of tuples ("sector", "point")
    """
    def calculate_configuration_avg_rtt(configuration):
        avg_rtt = 0.0
        total_datapoints = 0
        for location_a in configuration:
            for location_b in configuration:
                if location_a[0] != location_b[0]:
                    avg_rtt += rtt_mapping.get(location_a, location_b)
                    total_datapoints += 1
        return avg_rtt / total_datapoints

    """
    :param configuration: Set of tuples ("sector", "point")
    """
    all_configurations = []
    def find_optimal(sectors_left, configuration):
        if len(sectors_left) == 0:
            configuration = list(configuration)
            configuration.sort(key=lambda x: x[0])

            result = (configuration, calculate_configuration_avg_rtt(configuration))
            all_configurations.append(result)
            return result

        cur_sector = sectors_left[0]
        sectors_left = sectors_left[1:]

        optimal_configuration = []
        optimal_rtt = 2**31 - 1
        for location in cur_sector:
            if location not in configuration:
                new_config = configuration.copy()
                new_config.add(location)
                found_config, config_rtt = find_optimal(sectors_left, new_config)
                if config_rtt < optimal_rtt:
                    optimal_rtt = config_rtt
                    optimal_configuration = found_config

        return (optimal_configuration, optimal_rtt)

    find_optimal(sector_list, set())
    all_configurations.sort(key=lambda x: x[1])
    return all_configurations

def read_options():
    parser = argparse.ArgumentParser(description="Find the optimal configuration based on callculated RTTS")
    parser.add_argument("calculated_rtt_file", type=str, help="file with calculated RTTs between all points")
    parser.add_argument("output_file", type=str, help="file to output evaluated results and found optimal configuration")
    parser.add_argument("-e", "--exclude", type=str, default="", help="comma seperated list of sectors to exclude")
    parser.add_argument("-r", "--redundant", type=str, default="", help="comma seperated list of [Sector]=N key,pair values indicating the number of ground stations to choose per sector. Default 1 per")

    args = parser.parse_args()
    return args

def create_sector_list(redundancies, sect_point_map):
    """
    :param redundancies: A dictionary mapping sectors(str) to number of redundant points to pick from it
    :param sect_point_map: A dictionary mapping sectors(str) to points(str)
    :return: A list of tuples (Sector Name, Point Name)
    """
    sector_list = []
    for sector in sect_point_map:
        point_list = []
        for point in sect_point_map[sector]:
            point_list.append((sector, point))
        for i in range(redundancies[sector]):
            sector_list.append(point_list)
    return sector_list

def preprocess_input(args, rtt_filename):
    exclusion_sectors = []
    if args.exclude != "":
        exclusion_sectors = args.exclude.split(",")

    redundancies = defaultdict(lambda: 1)
    if args.redundant != "":
        for item in args.redundant.split(","):
            sector, repetitions = item.split("=")
            redundancies[sector] = int(repetitions)

    rtt_mapping = None
    sector_point_names = None
    with open(rtt_filename, "r") as fp:
        sector_point_names, rtt_mapping = read_rtt_data(fp)

    for sector in exclusion_sectors:
        del sector_point_names[sector]

    sector_list = create_sector_list(redundancies, sector_point_names)
    return (sector_list, rtt_mapping)

def main():
    args = read_options()
    rtt_filename = os.path.abspath(args.calculated_rtt_file)
    output_filename = os.path.abspath(args.output_file)

    sector_list, rtt_mapping = preprocess_input(args, rtt_filename)
    configurations = find_optimal_configuration(sector_list, rtt_mapping)

    print("Optimal Configuration: " + str(configurations[0]))
    with open(output_filename, "w") as fp:
        for i in range(len(configurations)):
            config = configurations[i]
            line = str(i+1) + ", " + "Configuration: " + str(config[0]) + " | Average RTT->" + str(config[1]) + "\n"
            fp.write(line)


if __name__ == "__main__":
    main()
