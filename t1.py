
import json
import re

# Function to convert formatted string to dictionary
def convert_to_dict(txt):
    result = {}
    lines = txt.split('\n')
    for line in lines:
        if line:
            print(line)
            vyos, nixos = line.split('@')
            vyos_parts = vyos.split('=')
            vyos_path = vyos_parts[0].split('#')
            vyos_value = vyos_parts[1] if len(vyos_parts) > 1 else None
            nixos_parts = nixos.split('=')
            nixos_path = nixos_parts[0].split('.')
            nixos_value = nixos_parts[1] if len(nixos_parts) > 1 else None

            curr_dict = result
            for part in vyos_path[:-1]:
                if not part in curr_dict:
                    curr_dict[part] = {}
                curr_dict = curr_dict[part]
            last_vyos_key = vyos_path[-1]
            if not last_vyos_key in curr_dict:
                curr_dict[last_vyos_key] = {}

            curr_dict = curr_dict[last_vyos_key]
            for part in nixos_path:
                if not part in curr_dict:
                    curr_dict[part] = {}
                curr_dict = curr_dict[part]
            curr_dict["vyosValue"] = vyos_value
            curr_dict["nixosPath"] = nixos

    return result

# Load text from a file or a string
txt = """
interfaces#bonding#$0#hash-policy=$1@networking.bonds.$0.driverOptions.xmit_hash_policy="$1";
interfaces#bonding#$0#member#interface=$1@networking.bonds.$0.interfaces=$1;
interfaces#bonding#$0#mode=$1@networking.bonds.$0.driverOptions.mode="$1";
interfaces#bonding#$0#primary=$1@networking.bonds.$0.driverOptions.primary="$1";
interfaces#bonding#$0#arp-monitor#interval=$1@networking.bonds.$0.driverOptions.arp_interval="$1";
interfaces#bonding#$0#arp-monitor#target=$1@networking.bonds.$0.driverOptions.apr_ip_target="$1";
interfaces#ethernet#$0#address=^dhcp$@networking.interfaces.$0.useDHCP=true;
interfaces#wireguard#$0#peer#client#address=$1;interfaces#wireguard#$2#port=$3@networking.wireguard.interfaces.$0.peers.endpoint=$1:$3;
"""

# Convert the formatted string to a dictionary
result = convert_to_dict(txt)

# Dump the dictionary to a JSON file
with open('output1.json', 'w') as json_file:
    json.dump(result, json_file, indent=2)


import json

# Function to convert formatted string to dictionary
def convert_to_dict(txt):
    result = {}
    lines = txt.split('\n')
    for line in lines:
        if line:
            vyos, nixos = line.split('@')
            vyos_parts = vyos.split('=')
            vyos_path = vyos_parts[0].split('#')
            vyos_value = vyos_parts[1] if len(vyos_parts) > 1 else None
            nixos_parts = nixos.split('=')
            nixos_path = nixos_parts[0].split('.')
            nixos_value = nixos_parts[1] if len(nixos_parts) > 1 else None

            curr_dict = result
            for part in vyos_path:
                if not part in curr_dict:
                    curr_dict[part] = {}
                curr_dict = curr_dict[part]
            curr_dict["vyosValue"] = vyos_value
            curr_dict["nixosPath"] = nixos

            if vyos_path != nixos_path:
                curr_dict["additionalVyOSPath"] = [f"{vyos_path[i]}={vyos_value}" for i in range(len(vyos_path), len(nixos_path))]

    return result

# Load text from a file or a string
txt = """
interfaces#bonding#$0#hash-policy=$1@networking.bonds.$0.driverOptions.xmit_hash_policy="$1";
interfaces#bonding#$0#member#interface=$1@networking.bonds.$0.interfaces=$1;
interfaces#bonding#$0#mode=$1@networking.bonds.$0.driverOptions.mode="$1";
interfaces#bonding#$0#primary=$1@networking.bonds.$0.driverOptions.primary="$1";
interfaces#bonding#$0#arp-monitor#interval=$1@networking.bonds.$0.driverOptions.arp_interval="$1";
interfaces#bonding#$0#arp-monitor#target=$1@networking.bonds.$0.driverOptions.apr_ip_target="$1";
interfaces#ethernet#$0#address=^dhcp$@networking.interfaces.$0.useDHCP=true;
interfaces#wireguard#$0#peer#client#address=$1;interfaces#wireguard#$2#port=$3@networking.wireguard.interfaces.$0.peers.endpoint=$1:$3;
"""

# Convert the formatted string to a dictionary
result = convert_to_dict(txt)

# Dump the dictionary to a JSON file
with open('output2.json', 'w') as json_file:
    json.dump(result, json_file, indent=2)
