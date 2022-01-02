import os
import sys
import csv
import argparse
sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("../../rtt_simulator"))
sys.path.append(os.path.abspath("../../satgenpy"))

from sim_config import SimulationConfig
from helper import PNWMixedNetworkRTTSimulator, retrieve_network_state

def read_options():
    parser = argparse.ArgumentParser(description="Simulate RTT time for a mixed ground-satellite network in the PNW")
    parser.add_argument("-g", "--gen-state", action="store_true", help="generate the required network state")
    parser.add_argument("-r", "--run", action="store_true", help="run simulation")
    parser.add_argument("config", type=str, help="simulation config file")
    parser.add_argument("path", type=str, help="folder to run simulation in and store generated state")

    args = parser.parse_args()
    return args

def main():
    args = read_options()
    config_path = os.path.abspath(args.config)
    sim_path = os.path.abspath(args.path)

    config = SimulationConfig(config_path)

    if not os.path.exists(sim_path):
        os.mkdir(sim_path)

    gs_map = retrieve_network_state(config, sim_path, gen_state=args.gen_state)


    if args.run:
        rtt_file_path = sim_path + "/calculated_rtts.txt"
        simulator = PNWMixedNetworkRTTSimulator(config, sim_path, gs_map)

        with open(rtt_file_path, 'w') as fp:
            writer = csv.writer(fp)
            i = 0
            for rtt in simulator.generate_rtts():
                writer.writerow([i, rtt])
                i += 1

if __name__ == "__main__":
    main()
