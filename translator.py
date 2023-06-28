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

for key, value in daten["interfaces"]["ethernet"].items():
    print(key)

ETH_INTERFACES = daten["interfaces"]["ethernet"]

# Bond interfaces
if "bonding" in daten["interfaces"]:
    BOND_INTERFACES = daten["interfaces"]["bonding"]
else: 
    BOND_INTERFACES = {}



# DHCP information

# Wireguard information
# BGP information 

# User 

""" create nixos configuration with collected data """

nixBondConf = []

for key in BOND_INTERFACES:
    tempBondConf = f"interfaces.{key} = {{useDHCP = }}"
    print(tempBondConf)




condition = False
value = 10

template = f"Result: {'Condition is True' if condition else 'Condition is False'}, Value: {value}"
result = template  # Assigns the concatenated string to 'result'
print(result)
