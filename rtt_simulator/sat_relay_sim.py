import sys
sys.path.append(os.path.abspath("../satgenpy"))

import satgen
import os
import random
import string
import shutil
import tempfile
import sim_config
import constants
from collections import defaultdict
from satgen.post_analysis.print_routes_and_rtt import print_routes_and_rtt

def SatelliteNetworkState():
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
            writer = csv.writer(fp, delimeter=",", quotechar="\"", \
                    quoting=csv.QUOTE_MINIMAL)

            id = 0
            for net_point in self.groundstation_points:
                if net_point.type() == constants.GS_POINT_TYPE:
                    gs_name = net_point.name()
                    row = [id, gs_name] + net_point.location() + [0.0]
                    writer.write_row(row)
                    self.loc_to_id[gs_name] = id
                    id += 1

        return tmp_name

    def create(self):
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        tmp_gs_fname = self.__create_tmp_gs_config()

        satgen.extend_ground_stations(tmp_gs_fname, self.output_dir+"/ground_stations.txt")
        os.remove(tmp_gs_fname)
        satgen.generate_tles_from_scratch_manual(
            self.output_dir + "/tles.txt",
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
            self.output_dir + "/isls.txt",
            self.constellation.num_orbs,
            self.constellation.num_sats_per_orb,
            isl_shift=0,
            idx_offset=0
        )
        satgen.generate_description(
            self.output_dir + "/description.txt",
            self.constellation.max_gsl_length_m,
            self.constellation.max_isl_length_m
        )

        ground_stations = satgen.read_ground_stations_extended(
            self.output_dir + "/ground_stations.txt"
        )
        satgen.generate_simple_gsl_interfaces_info(
            self.output_dir + "/gsl_interfaces_info.txt",
            self.constellation.num_orbs * self.constellation.num_sats_per_orb,
            len(ground_stations),
            1,
            1,
            1,
            1
        )
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
        return GroundstationMap(save_to_fname, gs_map=self.loc_to_id)

    def cleanup(self):
        shutil.rmtree(self.output_dir)

class GrounstationMap():
    def __init__(self, gs_fname, gs_map=None):
        self.name_to_id_map = gs_map
        self.fname = gs_fname

    def load(self):
        if not os.path.exists(self.fname):
            raise ValueError("No such file '" + self.fname + "' to load from")
        if not os.access(self.fname, os.R_OK):
            raise ValueError("Access Denied to read file '" + self.fname + "'")

        self.name_to_id_map = {}
        try:
            with open(self.fname, "r") as fp:
                reader = csv.reader(fp)
                for row in reader:
                    self.name_to_id_map[int(row[0])] = row[1]
        except:
            raise IOError("Unexpected Error reading '" + self.fname + "': " + str(self.exc_info()[0]))

    def save(self):
        if self.fname is None:
            raise ValueError("No write filename was specified")

        try:
            with open(self.fname, "w") as fp:
                writer = csv.writer(fp, delimiter=",", quotechar="\"", quoting=csv.QUOTE_MINIMAL)
                for id, gs_name in self.name_to_id_map.items():
                    writer.write_row([id, gs_name])
        except:
            raise IOError("Unexpected Error reading '" + self.fname + "': " + str(self.exc_info()[0]))

    def get_groundstation_id(self, name):
        if self.name_to_id_map is None:
            raise ValueError("No groundstation name to ID map has been loaded")
        if name not in self.name_to_id_map:
            raise ValueError("No ID associated with '" + name + "'")
        return self.name_to_id_map[name]


class SatelliteRelaySimulator():
    def __init__(self, gs_map, duration, state_dir, output_dir):
        self.state_dir = state_dir
        self.output_dir = output_dir
        self.duration = duration
        self.rtt_datapoints = None
        self.gs_name_to_id_map = gs_map

    def run(self, src_name, dst_name):
        src_id = self.gs_name_to_id_map.get_groundstation_id(src_name)
        dst_id = self.gs_name_to_id_map.get_groundstation_id(dst_name)
        print_routes_and_rtt(self.output_dir, self.state_dir, constants.TIMESTEP_MS, self.duration, src_id, dst_id, "")

        rtt_filename = self.output_dir + "/" + str(constants.TIMESTEP_MS) + "ms_for_" + str(self.duration) + "s/" + \
            "manual/data/networkx_rtt_" + str(src_id) + "_to_" + str(dst_id)

        with open(rtt_filename, "r") as rtt_file:
            reader = csv.reader(rtt_file)
            self.rtt_datapoints = []
            for row in reader:
                rtt_in_seconds = float(row[1]) / 1000000000.0
                self.rtt_datapoints.append(rtt_in_seconds)

    def all_rtts(self):
        for rtt_in_s in self.rtt_datapoints:
            yield rtt_in_s

    def avg_rtt(self):
        avg = 0.0
        for rtt_in_s in self.all_rtts():
            avg += rtt_in_s
            total += 1

        avg /= float(total)
        return avg

    def cleanup(self):
        shutil.rmtree(self.output_dir)
