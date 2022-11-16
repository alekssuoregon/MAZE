import sys
import os
sys.path.append(os.path.abspath("../tools"))
sys.path.append(os.path.abspath("../rtt_simulator"))

import sim_config
import constants

def test_sim_config():
    fname = os.path.abspath("./example_config.json")
    config = sim_config.SimulationConfig(fname)

    correct_order = {
        "P1": ["Seattle", "Portland", "San Francisco", "Los Angeles"],
        "P2": ["Seattle", "Los Angeles", "San Francisco", "Portland"]
    }
    correct_points = {
        "Seattle": {
            "type": constants.CITY_POINT_TYPE,
            "location": (47.6062, 122.3321)
        },
        "Portland": {
            "type": constants.GS_POINT_TYPE,
            "location": (45.5152, 122.6784)
        },
        "San Francisco": {
            "type": constants.GS_POINT_TYPE,
            "location": (37.7749, 122.4194)
        },
        "Los Angeles": {
            "type": constants.CITY_POINT_TYPE,
            "location": (34.0522, 118.2437)
        }
    }

    point_count = 0
    for point in config.all_points():
        name = point.name()
        assert point.type() == correct_points[name]["type"]
        assert point.location() == correct_points[name]["location"]
        point_count += 1

    assert point_count == 4

    sub_sims = config.sub_simulations()
    for path_name in sub_sims:
        sub_sim_config = sub_sims[path_name]
        assert path_name in ["P1", "P2"]
        assert sub_sim_config.duration() == 1
        assert sub_sim_config.constellation().name == "Starlink_550"

        i = 0
        for point in sub_sim_config.network_points():
            name = point.name()
            assert (name == correct_order[path_name][i] and name in correct_points)
            assert point.type() == correct_points[name]["type"]
            assert point.location() == correct_points[name]["location"]
            i += 1
