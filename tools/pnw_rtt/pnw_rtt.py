import os
import sys
import csv
import logging
import argparse
sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("../../rtt_simulator"))
sys.path.append(os.path.abspath("../../satgenpy"))

from sim_config import SimulationConfig
from helper import PNWMixedNetworkPathRTTSimulator, PNWMixedNetworkEveryPairRTTSimulator, retrieve_network_state

def read_options():
    parser = argparse.ArgumentParser(description="Simulate RTT time for a mixed ground-satellite network in the PNW")
    parser.add_argument("-g", "--gen-state", action="store_true", help="generate the required network state")
    parser.add_argument("-r", "--run", action="store_true", help="run simulation")
    parser.add_argument("-a", "--all-pairs", action="store_true", help="Calculate RTT between all pairs of nodes not just a simple path")
    parser.add_argument("config", type=str, help="simulation config file")
    parser.add_argument("path", type=str, help="folder to run simulation in and store generated state")

    args = parser.parse_args()
    return args

def main():
    args = read_options()
    config_path = os.path.abspath(args.config)
    sim_path = os.path.abspath(args.path)

    try:
        config = SimulationConfig(config_path)
    except ValueError as e:
        logging.error("Failed to load simulation config file '" + config_path + "' -> " + str(e))
        return

    if not os.path.exists(sim_path):
        os.mkdir(sim_path)

    try:
        gs_map = retrieve_network_state(config, sim_path, gen_state=args.gen_state)
    except ValueError as e:
        logging.error("Failed to retrieve satellite network state -> " + str(e))
        return

    if args.run:
        logging.info("Calculating Round Trip Time for specified mixed-network path...")
        rtt_file_path = sim_path + "/calculated_rtts.txt"
        simulator = None
        if args.all_pairs:
            simulator = PNWMixedNetworkEveryPairRTTSimulator(config, sim_path, gs_map)
        else:
            simulator = PNWMixedNetworkPathRTTSimulator(config, sim_path, gs_map)

        avg_rtt = [0 for _ in range(len(simulator.get_param_order()))]
        try:
            with open(rtt_file_path, 'w') as fp:
                writer = csv.writer(fp)
                writer.writerow(["timestep"] + list(simulator.get_param_order()))
                i = 0
                for rtt in simulator.generate_rtts():
                    for i in range(len(rtt)):
                        avg_rtt[i] += rtt[i]
                    writer.writerow([i] + list(rtt))
                    i += 1
            logging.info("Simulation results written to " + rtt_file_path)
        except OSError as e:
            logging.error("Failed to write simulation results to " + rtt_file_path + " -> " + str(e))
            return


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
