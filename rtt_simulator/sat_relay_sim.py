import sys
import os
sys.path.append(os.path.abspath("../satgenpy"))

import satgen
import random
import string
import shutil
import csv
import tempfile
import constants
from collections import defaultdict
from network_simulator import NetworkSimulator
from satgen.post_analysis.print_routes_and_rtt import print_routes_and_rtt

class SatelliteNetworkState():
    """
    SatelliteNetworkState generates a LEO satellite constellation using the
    Hypatia framework

    :param constellation_config.ConstellationConfig constellation_config: An
        object describing the satellite constellation
    :param gs_points: A generator object the yields net_point.NetworkPoint objects
    :param int duration: Duration of the simulation in seconds
    :param str output_dir: The folder to save the generated state to
    """
    #gs_points is a generator of NetworkPoints
    def __init__(self, constellation_config, gs_points, duration, output_dir):
        self.constellation = constellation_config
        self.groundstation_points = gs_points
        self.output_dir = output_dir
        self.duration = duration
        self.loc_to_id = defaultdict(lambda: -1)

    def __create_tmp_gs_config(self):
        tmp_name = self.output_dir + "/tmp_gs_loc.csv"
        with open(tmp_name, "w") as fp:
            writer = csv.writer(fp, delimiter=",", quotechar="\"", \
                    quoting=csv.QUOTE_MINIMAL)

            id = 0
            node_inc = self.constellation.num_orbs * self.constellation.num_sats_per_orb
            for net_point in self.groundstation_points:
                if net_point.type() == constants.GS_POINT_TYPE:
                    gs_name = net_point.name()
                    row = [id, gs_name] + list(net_point.location()) + [0.0]
                    writer.writerow(row)
                    self.loc_to_id[gs_name] = node_inc + id
                    id += 1

        return tmp_name

    def create(self):
        """
        create generates the satellite network state
        """
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        tmp_gs_fname = self.__create_tmp_gs_config()

        write_to_dir = self.output_dir + "/" + self.constellation.name
        os.mkdir(write_to_dir)

        satgen.extend_ground_stations(tmp_gs_fname, write_to_dir + "/ground_stations.txt")

        with open(write_to_dir + "/ground_stations.txt") as fp:
            all_str = fp.read()
            print(all_str)

        os.remove(tmp_gs_fname)
        satgen.generate_tles_from_scratch_manual(
            write_to_dir + "/tles.txt",
            self.constellation.name,
            self.constellation.num_orbs,
            self.constellation.num_sats_per_orb,
            self.constellation.phase_diff,
            self.constellation.inclination_degree,
            self.constellation.eccentricity,
            self.constellation.arg_of_preigee_degree,
            self.constellation.mean_motion_rev_per_day
        )
        satgen.generate_plus_grid_isls(
            write_to_dir + "/isls.txt",
            self.constellation.num_orbs,
            self.constellation.num_sats_per_orb,
            isl_shift=0,
            idx_offset=0
        )
        satgen.generate_description(
            write_to_dir + "/description.txt",
            self.constellation.max_gsl_length_m,
            self.constellation.max_isl_length_m
        )

        ground_stations = satgen.read_ground_stations_extended(
            write_to_dir + "/ground_stations.txt"
        )
        satgen.generate_simple_gsl_interfaces_info(
            write_to_dir + "/gsl_interfaces_info.txt",
            self.constellation.num_orbs * self.constellation.num_sats_per_orb,
            len(ground_stations),
            1,
            1,
            1,
            1
        )

        for f in os.listdir(write_to_dir):
            print(f)

        satgen.help_dynamic_state(
            self.output_dir,
            constants.HYPATIA_NUM_THREADS,
            self.constellation.name,
            constants.TIMESTEP_MS,
            self.duration,
            self.constellation.max_gsl_length_m,
            self.constellation.max_isl_length_m,
            constants.DYNAMIC_STATE_ALGORITHM,
            True
        )

    def groundstation_map(self, save_to_fname=None):
        """
        groundstation_map returns an object mapping ground station node names
        to their internal simulation IDs

        :param str save_to_fname: The file name to save the groundstation map to
        :return: GroundstationMap object
        """
        return GroundstationMap(save_to_fname, gs_map=self.loc_to_id)

    def cleanup(self):
        """
        cleanup removes the generated satellite state files
        """
        shutil.rmtree(self.output_dir)

class GroundstationMap():
    """
    GroundstationMap holds information mapping ground station network nodes
    to their internal simulation ID

    :param str gs_fname: The filename to store/load the mapping to/from
    :param dict gs_map: The dictionary object containing the (Name, ID) mapping
    """
    def __init__(self, gs_fname, gs_map=None):
        self.name_to_id_map = gs_map
        self.fname = gs_fname

    def load(self):
        """
        load reads the gs_fname file and attempts to load the mapping into memory

        :raises ValueError: If invalid file name is provided
        :raises IOError: If unable to read gs_fname
        """
        if self.gs_fname is None or not os.path.exists(self.fname):
            raise ValueError("Unable to load groundstation mapping, invalid ground station mapping file provided")

        self.name_to_id_map = {}
        try:
            with open(self.fname, "r") as fp:
                reader = csv.reader(fp)
                for row in reader:
                    self.name_to_id_map[row[0]] = int(row[1])
        except:
            raise IOError("Unexpected Error reading '" + self.fname + "': " + str(self.exc_info()[0]))

    def save(self):
        """
        save stores the ground station mapping to disk at gs_fname

        :raises ValueError: If no gs_fname was provided
        :raises IOError: If unable to write to gs_fname
        """
        if self.fname is None:
            raise ValueError("No write filename was specified")

        try:
            with open(self.fname, "w") as fp:
                writer = csv.writer(fp, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
                for id, gs_name in self.name_to_id_map.items():
                    writer.writerow([id, gs_name])
        except:
            raise IOError("Unexpected Error reading '" + self.fname + "': " + str(self.exc_info()[0]))

    def get_groundstation_id(self, name):
        """
        get_groundstation_id returns the internal simulation ID of the provided
        ground statio node name

        :param str name: Name of the node to lookup
        :raises ValueError: If no map has been loaded or lookup fails
        :return: int ID of node
        """
        if self.name_to_id_map is None:
            raise ValueError("No groundstation name to ID map has been loaded")
        if name not in self.name_to_id_map:
            raise ValueError("No ID associated with '" + name + "'")
        return self.name_to_id_map[name]


class SatelliteRelaySimulator(NetworkSimulator):
    """
    SatelliteRelaySimulator implements the network_simulator.NetworkSimulator
    interface and generates Round Trip Times between two ground stations accross
    a LEO satellite constellation

    :param GroundstationMap gs_map: An object mapping ground station node names
        to internal simulator IDs used by Hypatia
    :param int duration: Duration of the simulation in seconds
    :param str state_dir: Path to the directory containing the generated satellite
        network state
    :param str output_dir: Directory to write the calculated RTTs to
    :param str satgenpy_dir: Full path to the hypatia satgenpy module
    """
    def __init__(self, gs_map, duration, state_dir, output_dir, satgenpy_dir):
        self.state_dir = state_dir
        self.output_dir = output_dir
        self.duration = duration
        self.rtt_datapoints = None
        self.gs_name_to_id_map = gs_map
        self.satgenpy_dir = satgenpy_dir

    """
    src, dst are NetworkPoints
    """
    def generate_rtts(self, src, dst):
        """
        generate_rtts calculates and returns the Round Trip Times between
        the provided source and destination ground station network nodes

        :param net_point.NetworkPoint src: Source ground station
        :param net_point.NetworkPoint dst: Destination ground station
        :return: A generator object that yields RTTs in milliseconds
        """
        src_id = self.gs_name_to_id_map.get_groundstation_id(src.name())
        dst_id = self.gs_name_to_id_map.get_groundstation_id(dst.name())
        print_routes_and_rtt(self.output_dir, self.state_dir, constants.TIMESTEP_MS, self.duration, src_id, dst_id, self.satgenpy_dir + "/")

        for f in os.listdir(self.output_dir):
            print(f)
        rtt_filename = self.output_dir + "/data/networkx_rtt_" + str(src_id) + "_to_" + str(dst_id) + ".txt"

        with open(rtt_filename, "r") as rtt_file:
            reader = csv.reader(rtt_file)
            self.rtt_datapoints = []
            for row in reader:
                rtt_in_ms = float(row[1]) / 1000000.0
                self.rtt_datapoints.append(rtt_in_ms)

        return (rtt_in_s for rtt_in_s in self.rtt_datapoints)

    def cleanup(self):
        """
        cleanup deletes all files generated by the simulator
        """
        shutil.rmtree(self.output_dir)
