import sys
import satgen
import os
import random
import string
import shutil
import tempfile
import sim_config
import constants
from satgen.post_analysis.analyze_rtt import analyze_rtt

def SatelliteNetworkState():
    def __init__(self, constellation_config, duration, output_dir):
        self.constellation = constellation_config
        self.output_dir = output_dir
        self.duration = duration

    def __create_tmp_gs_config(self):
        tmp_name = self.output_dir + "/tmp_gs_loc.csv"
        with open(tmp_name, "w") as fp:
            writer = csv.writer(fp, delimeter=",", quotechar="\"", \
                    quoting=csv.QUOTE_MINIMAL)

            id = 0
            for net_point in self.config.network_points():
                if net_point.type() == constants.GS_POINT_TYPE:
                    row = [id, net_point.name()] + net_point.location() + [0.0]
                    writer.write_row(row)
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


class RelaySimulator():
    def __init__(self, config):
        self.config = config
        self.state_dirpath = tempfile.mkdtemp()
        self.sim_state = SatelliteNetworkState(self.config.constellation(), self.state_dirpath)

    def run(self):
        state_dir = tempfile.mkdtemp()
        sim_state = SatelliteNetworkState(self.config.constellation(), self.config.duration, state_dir)
        sim_state.create()
        analyze_rtt(self.config.output_dir, state_dir, constants.HYPATIA_NUM_THREADS, self.config.duration)
        shutil.rmtree(state_dir)
