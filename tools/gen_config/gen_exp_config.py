import json
import argparse
import os

_BASE_CONFIG = {
    "SimulationName": "",
    "SimulationDuration": 50,
    "NetworkPoint": {},
    "NetworkOrder": [],
    "Constellation": "Starlink"
}

def read_options():
    parser = argparse.ArgumentParser(description="Generate simulation config for sector based experiment")
    parser.add_argument("sector_config", type=str, help="config file location")
    parser.add_argument("output_config", type=str, help="generated config file")

    args = parser.parse_args()
    return args

def is_valid_entry(line):
    def is_float(num_str):
        try:
            float(num_str)
            return True
        except:
            return False

    items = line.split(",")
    return len(items) == 2 and is_float(items[0]) and is_float(items[1])


def main():
    args = read_options()
    in_config_path = os.path.abspath(args.sector_config)
    out_config_path = os.path.abspath(args.output_config)

    output_config = {
        "SimulationName": "None",
        "SimulationDuration": 50,
        "NetworkPoints": {},
        "NetworkOrder": [],
        "Constellation": "Starlink"
    }
    cur_prefix = ""
    cur_position = 1
    with open(in_config_path, "r") as fp:
        for line in fp:
            line = line.strip()
            if line.startswith("PREFIX="):
                cur_prefix = line.replace("PREFIX=", "")
                cur_position = 1
            elif is_valid_entry(line):
                latitude, longitude = [float(item) for item in line.split(",")]
                net_point = {
                    "Type": "GroundStation",
                    "Location": {
                        "Latitude": latitude,
                        "Longitude": longitude
                    }
                }
                point_name = cur_prefix + "_point" + str(cur_position)
                output_config["NetworkPoints"][point_name] = net_point
                output_config["NetworkOrder"].append(point_name)
                cur_position += 1

    str_output = json.dumps(output_config, indent=4)
    with open(out_config_path, "w") as fp:
        fp.write(str_output)

    print("Config written to " + out_config_path)

if __name__ == "__main__":
    main()
