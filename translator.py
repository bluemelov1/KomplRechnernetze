import json


# get vyos file 
path = "szenario1/vyos/bonding/config.json"

# Öffne und lade die JSON-Datei in ein Python-Objekt
with open(path, 'r') as f:
    daten = json.load(f)

""" retrive all information out of vyos json"""
# Hostname
HOST_NAME = daten["system"]["host-name"]

# Interfaces (problem because eth0 -> enp0s9 is always different)
INTERFACES = []

for key, value in daten["interfaces"].items():
    print(key)
    print(value)

# Bond interfaces
# DHCP information
# Wireguard information
# BGP information 

# User 

""" create nixos configuration with collected data """

