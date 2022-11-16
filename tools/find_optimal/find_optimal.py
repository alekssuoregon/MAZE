import csv
import argparse
import os
from collections import defaultdict
import statistics

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

    def remove(self, sector):
        del self._map[sector]
        for sect in self._map:
            for point in self._map[sect]:
                if sector in self._map[sect][point]:
                    del self._map[sect][point][sector]

    def get(self, source, dest):
        left, right = self._find_key_order(source, dest)
        return self._map[left[0]][left[1]][right[0]][right[1]]

    def print(self):
        for sector in self._map:
            for point in self._map[sector]:
                for s2 in self._map[sector][point]:
                    for p2 in self._map[sector][point][s2]:
                        print(sector + "," + point + "->" + s2 + "," + p2 + "=" + str(self._map[sector][point][s2][p2]))

def get_optimal_configuration(avg_map):
    configuration = {}
    for sect, points in avg_map.items():
        best_point = ""
        min_rtt = 2**32 - 1
        for point, rtt in points.items():
            if rtt < min_rtt:
                best_point = point
                min_rtt = rtt
        configuration[sect] = (best_point, min_rtt)
    return configuration


def read_rtt_data(fp):
    headers = fp.readline().strip().split(",")[1:]
    rtts = [0.0 for _ in range(len(headers))]

    total_entries = 0
    for line in fp:
        entry = line.strip().split(",")
        total_entries += 1
        for i in range(1, len(entry)):
            rtts[i-1] += float(entry[i])

    for i in range(len(rtts)):
        rtts[i] /= total_entries


    points_map = defaultdict(lambda: defaultdict(lambda: []))
    for i in range(len(headers)):
        p1, p2 = headers[i].split("/")
        sect1, point1 = p1.split("_")
        sect2, point2 = p2.split("_")
        points_map[sect1][point1].append(rtts[i])
        points_map[sect2][point2].append(rtts[i])

    avg_map = defaultdict(lambda: defaultdict(lambda: 0.0))
    for sect, points in points_map.items():
        for point, values in points.items():
            avg_map[sect][point] = statistics.fmean(values)
    return avg_map


def run(filename):
    avg_rtts = None
    with open(filename, 'r') as fp:
        avg_rtts = read_rtt_data(fp)
    return get_optimal_configuration(avg_rtts)
"""
def read_rtt_data(fp):
    :param fp: File pointer
    :return: (Dictionary mapping Sectors->points and Dictionary RTTSectorPointMap object)
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
"""

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
        rtt_mapping.remove(sector)

    sector_list = create_sector_list(redundancies, sector_point_names)
    return (sector_list, rtt_mapping)

def create_output(optimal_config):
    keys = []
    for key, _ in optimal_config.items():
        keys.append(key)
    keys.sort(key=lambda x: int(x.lstrip("Sector")))

    line1 = []
    line2 = []
    total_avg = 0.0
    for key in keys:
        print(key + " -> " + optimal_config[key][0])
        line1.append(optimal_config[key][0])
        line2.append(str(optimal_config[key][1]))
        total_avg += optimal_config[key][1]
    print("Average RTT: " + str(total_avg / len(keys)))

    return ','.join(keys) + '\n' + ','.join(line1) + '\n' + ','.join(line2)

def main():
    args = read_options()
    rtt_filename = os.path.abspath(args.calculated_rtt_file)
    output_filename = os.path.abspath(args.output_file)

    """
    sector_list, rtt_mapping = preprocess_input(args, rtt_filename)
    configurations = find_optimal_configuration(sector_list, rtt_mapping)
    """
    optimal = run(rtt_filename)
    output = create_output(optimal)

    print("Optimal Configuration: ", optimal)
    with open(output_filename, "w") as fp:
        fp.write(output)


if __name__ == "__main__":
    main()
