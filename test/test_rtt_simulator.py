import sys
import os
import tempfile
sys.path.append(os.path.abspath("./rtt_simulator"))

import sat_relay_sim
import constants
import constellation_config

def test_sat_sim():
    stated_dir = os.path.abspath("./starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls_test")

    gmap = sat_relay_sim.GroundstationMap(state_dir + "/" + id_map)
    gmap.load()


    with tempfile.TemporaryDirectory() as tempdir_name:
        duration = 200 #seconds
        src_name = "start"
        dst_name = "end"

        simulator = sat_relay_sim.SatelliteRelaySimulator(gmap, duration, state_dir, tempdir_name)
        simulator.run(src_name, dst_name)

        src_id = gmap.get_groundstation_id(src_name)
        dst_id = gmap.get_groundstation_id(dst_name)
        rtt_fname = tempdir_name + "/" + str(constants.TIMESTEP_MS) + "ms_for_" + str(duration) + "s/" + \
            "manual/data/networkx_rtt_" + str(src_id) + "_to_" + str(dst_id)

        #Make sure simulator.run created the output file
        assert os.file.exists(rtt_fname)

        total = 0
        avg = 0.0
        for rtt in simulator.all_rtts():
            avg += rtt
            total += 1
        avg /= total

        #Make sure simulator generated all 2000 datapoints
        assert total == 2000

        #Make sure average rtt calculation is correct
        assert simulator.avg_rtt() == avg

def test_sat_state_gen():
    const_config = constellation_config.GetStarlinkConfig()
    netpoints = (net_point for net_point in [ \
        NetworkPoint("Tokyo", constants.GS_POINT_TYPE, "Tokyo", lat=35.6895, long=139.69171), \
        NetworkPoint("Shanghai", constants.GS_POINT_TYPE, "Shanghai", lat=31.22222, long=121.45806 \
        ])

    with tempfile.TemporaryDirectory() as tempdir_name:
        net_state = sat_relay_sim.SatelliteNetworkState(const_config, netpoints, 1, tempdir_name)
        net_state.create()

        assert os.file.exists(tempdir_name + "/ground_stations.txt")
        assert os.file.exists(tempdir_name + "/isls.txt")
        assert os.file.exists(tempdir_name + "/description.txt")
        assert os.file.exists(tempdir_name + "/gsl_interfaces_info.txt")

        gmap = net_state.groundstation_map()

        with tempfile.TemporaryDirectory() as sim_tempdir_name:
            sat_sim = sat_relay_sim.SatelliteRelaySimulator(gmap, 1, tempdir_name, sim_tempdir_name)
            sat_sim.run()
            assert sat_sim.avg_rtt() > 0
