import json
import sys

# get vyos file 
# path = "szenario1/vyos/bonding/config.json"
path = sys.argv[1]

mapping = {
       'interfaces': {
           'eth0': 'eth0',
           'eth1': 'enp0s9',
           'eth2': 'eth2',
           'eth3': 'enp0s8',
           'eth4': 'eth4',
           # Weitere Interface-Mappings hier
        },
}

# NixOS config
nixos_config = ""

# Öffne und lade die JSON-Datei in ein Python-Objekt
with open(path, 'r') as f:
    data = json.load(f)

""" retrive all information out of vyos json"""
# Hostname
HOST_NAME = data["system"]["host-name"]
nixos_config += f'# Hostname\n'
nixos_config += f'networking.hostName = "{HOST_NAME}";\n'


# Interfaces
if 'interfaces' in data:
    # check if ethernet interfaces exist
    if 'ethernet' in data["interfaces"]:
        nixos_config += f'\n# Interfaces\n'
        # get interface name and interface config
        for vyos_interface_name, vyos_interface_config in data["interfaces"]["ethernet"].items():   
            # check interface mapping
            if vyos_interface_name in mapping["interfaces"]:
                # get nixos interface name from mapping
                nixos_interface_name = mapping["interfaces"][vyos_interface_name]
                # check address attribute exist
                if 'address' in vyos_interface_config:
                    # split IP address into address and subnetmask 
                    address = vyos_interface_config["address"][0].split("/")
                    # translate to nixos config
                    nixos_config += (
                        f'networking.interfaces.{nixos_interface_name}.ipv4.addresses = [{{\n'
                        f'  address = "{address[0]}";\n'
                        f'  prefixLength = "{address[1]}";\n'
                        f'}}];\n'
                    )

# Bond interfaces
if "bonding" in data["interfaces"]:
    BOND_INTERFACES = data["interfaces"]["bonding"]
else: 
    BOND_INTERFACES = {}



# DHCP information

# Wireguard information
# BGP information 
#check if bgp config exist
if 'bgp' in data["protocols"]:
    # enable frr daemon and open frr config section
    nixos_config += (

        f'\n# BGP\n'
        f'services.frr.bgp.enable = true;\n'
        f'services.frr.bgp.config = \'\'\n'
    )
    # check if AS number is specified
    if 'system-as' in data["protocols"]["bgp"]:
        # set AS nummber / open bgp router section
        nixos_config += f'  router bgp {data["protocols"]["bgp"]["system-as"]}\n'
    # set router settings
    # disable default policies --> workaround
    nixos_config += f'    no bgp ebgp-requires-policy\n'
    if 'parameters' in data["protocols"]["bgp"]:
        for parameter in data["protocols"]["bgp"]["parameters"]:
            if parameter == "router-id":
                # set router id
                nixos_config += f'    bgp router-id {data["protocols"]["bgp"]["parameters"]["router-id"]}\n' 
    # set neighbor settings 
    if 'neighbor' in data["protocols"]["bgp"]:
        for neighbor_addr, neighbor_config in data["protocols"]["bgp"]["neighbor"].items():
            if 'remote-as' in neighbor_config:
                nixos_config += f'  neighbor {neighbor_addr} remote-as {neighbor_config["remote-as"]}\n'    
    # set network settings
    if 'address-family' in data["protocols"]["bgp"]:
        if 'ipv4-unicast' in data["protocols"]["bgp"]["address-family"]:
            if 'network' in data["protocols"]["bgp"]["address-family"]["ipv4-unicast"]:
                for network_addr in data["protocols"]["bgp"]["address-family"]["ipv4-unicast"]["network"]:
                    nixos_config += f'  network {network_addr}/24\n'
    # redistribute connected --> workaround
    nixos_config += f'  redistribute connected\n'
    # close frr config section
    nixos_config += f'\'\''
            

    



print(nixos_config)

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
