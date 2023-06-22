import json
import sys


# get vyos file 
# path = "szenario1/vyos/bonding/config.json"
path = sys.argv[1]

# Öffne und lade die JSON-Datei in ein Python-Objekt
with open(path, 'r') as f:
    data = json.load(f)

""" retrive all information out of vyos json"""
# Hostname
HOST_NAME = data["system"]["host-name"]

# Interfaces (problem because eth0 -> enp0s9 is always different)
INTERFACES = data["interfaces"]
nixos_config = ""

print(data["interfaces"]["ethernet"]["eth1"]["address"][0])

if 'interfaces' in data:
    if 'ethernet' in data["interfaces"]:
        for interface_name, interface_config in data["interfaces"]["ethernet"].items():   
            if 'address' in interface_config:
                address = interface_config["address"][0].split("/")
                nixos_config += (
                    f'networking.interfaces.{interface_name}.ipv4.addresses = [{{\n'
                    f'  address = "{address[0]}";\n'
                    f'  prefixLength = "{address[1]}";\n'
                    f'}}];\n'
                )

print(nixos_config)
# Bond interfaces
# DHCP information
# Wireguard information
# BGP information 
PROTOCOLS = data["protocols"]["bgp"]


# User 

""" create nixos configuration with collected data """

