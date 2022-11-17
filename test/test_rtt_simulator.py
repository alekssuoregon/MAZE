import sys
import os
import tempfile
sys.path.append(os.path.abspath("../rtt_simulator"))

import sat_relay_sim
import constants
import constellation_config
import net_point
import terrestrial_simulator

def test_sat_sim():
    state_dir = os.path.abspath("./starlink_550_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls_test")

    gmap = sat_relay_sim.GroundstationMap(state_dir + "/id_map.csv")
    gmap.load()


    with tempfile.TemporaryDirectory() as tempdir_name:
        duration = 200 #seconds

        src = net_point.NetworkPoint("start", constants.GS_POINT_TYPE, "start", 0, 0)
        dst = net_point.NetworkPoint("end", constants.GS_POINT_TYPE, "end", 120, 120)
        simulator = sat_relay_sim.SatelliteRelaySimulator(gmap, duration, state_dir, tempdir_name)

        net_seg = net_segment.NetworkSegment(src, dst)
        net_segment.NetworkSegment.configure(simulator, None)

        rtts = net_seg.get_rtts()

        src_id = gmap.get_groundstation_id(src.name())
        dst_id = gmap.get_groundstation_id(dst.name())
        rtt_fname = tempdir_name + "/data/networkx_rtt_" + str(src_id) + "_to_" + str(dst_id) + ".txt"

        #Make sure simulator.run created the output file
        assert os.path.exists(rtt_fname)

        total = 0
        avg = 0.0
        for rtt in rtts:
            avg += rtt
            total += 1
        avg /= float(total)

        #Make sure simulator generated all 2000 datapoints
        assert total == 2000

        #Make sure average rtt calculation is correct
        print("test_sat_sim calculated vs given avg_rtt -> ", avg, " vs ", net_seg.avg_rtt())
        assert net_seg.avg_rtt() == avg

def test_sat_state_gen():
    const_config = constellation_config.GetStarlinkConfig()
    src = net_point.NetworkPoint("Tokyo", constants.GS_POINT_TYPE, "Tokyo", 35.6895, 139.69171)
    dst = net_point.NetworkPoint("Shanghai", constants.GS_POINT_TYPE, "Shanghai", 31.22222, 121.45806)
    netpoints = (net_point for net_point in [src, dst])

    with tempfile.TemporaryDirectory() as tempdir_name:
        net_state = sat_relay_sim.SatelliteNetworkState(const_config, netpoints, 1, tempdir_name)
        net_state.create()

        state_dir_name = tempdir_name + "/" + const_config.name
        assert os.path.exists(state_dir_name + "/ground_stations.txt")
        assert os.path.exists(state_dir_name + "/isls.txt")
        assert os.path.exists(state_dir_name + "/description.txt")
        assert os.path.exists(state_dir_name + "/gsl_interfaces_info.txt")

        gmap = net_state.groundstation_map()

        with tempfile.TemporaryDirectory() as sim_tempdir_name:
            sat_sim = sat_relay_sim.SatelliteRelaySimulator(gmap, 1, state_dir_name, sim_tempdir_name)

            net_seg = net_segment.NetworkSegment(src, dst)
            net_segment.NetworkSegment.configure(sat_sim, None)

            print("test_sat_state_gen avg_rtt -> ", net_seg.avg_rtt())
            assert sat_sim.avg_rtt() > 0

def test_dist_sim():
    seattle_loc = (47.6062, 122.3321)
    los_angeles_loc = (34.0522, 118.2437)
    portland_loc = (45.5152, 122.6784)

    seattle_to_la_km = terrestrial_simulator.DistanceBasedPingCalculator._crow_flies_distance(seattle_loc[0], \
        seattle_loc[1], los_angeles_loc[0], los_angeles_loc[1])
    assert int(seattle_to_la_km) == 1546

    seattle_to_la_rtt_ms = 32.986
    simulator = terrestrial_simulator.DistanceBasedPingCalculator(seattle_to_la_km, seattle_to_la_rtt_ms, 0)

    assert simulator.rtt_between(seattle_loc[0], seattle_loc[1], los_angeles_loc[0], los_angeles_loc[1]) == seattle_to_la_rtt_ms
    assert 5 - simulator.rtt_between(seattle_loc[0], seattle_loc[1], portland_loc[0], portland_loc[1]) < 0.1
