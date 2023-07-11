import copy
import ipaddress
import re
import json
import subprocess

import mainprocessor

##### DHCP paser und interface mapping hinzufgen uns ausführen 

# remove not found entries in configuration
def remove_subpattern_lines(input_string):
    lines = input_string.split("\n")
    result_lines = []
    for line in lines:
        if not re.search(r'\{\$.*?\}', line):
            result_lines.append(line)
    result_string = "\n".join(result_lines)
    return result_string


def get_dhcp_configuration(vyos_config):

    dhcpInformationMapping = {
        'service#dhcp-server#shared-network-name#$0#subnet#$1#domain-name' : '$nameserverName',
        'service#dhcp-server#shared-network-name#$0#subnet#$1#name-server' : '$nameserverAddresses',
        'service#dhcp-server#shared-network-name#$0#subnet#$1#range#$2#stop' : '$networkAddressSpaceEnd',
        'service#dhcp-server#shared-network-name#$0#subnet#$1#range#$2#start' : '$networkAddressSpaceStart',
        'interfaces#ethernet#$0#address' : '$interfaceInformation',
    }
    dhcpTemplate = 'dhcpTemplates/dhcpTemplate.txt' 
    subnetTemplatePath = 'dhcpTemplates/dhcpSubnetTemplate.txt'



    # list to store data
    dhcpExtractedData = []

    # iterate through VyOS config entries and check against the mapping
    for vyos_config_path in vyos_config:
        vyos_config_sep = vyos_config_path.split("=")
        vyos_config_keywords = vyos_config_sep[0].split("#")

        mapping_hit = copy.deepcopy(dhcpInformationMapping)
        args = {}

        checking_hit = mainprocessor.check(vyos_config_keywords, mapping_hit, args, 0)

        if checking_hit:
            dhcpExtractedData.append({
                "mapping" : mapping_hit,
                "args" : args,
                "vyos_config_value" : vyos_config_sep[1]
            })

    # print the checking result data
    for entry in dhcpExtractedData:
        print(entry)
    print(len(dhcpExtractedData))

    # initialize lists for value extraction
    nameserverName = []
    nameserverAddresses = []
    networkAddress = []
    networkAddressSpaceStart = []
    networkAddressSpaceEnd = []
    interfaceName = []
    interfaceAddress = []

    # extract the information and save to variables
    for entry in dhcpExtractedData:
        # Nameserver
        if '$nameserverName' in entry['mapping'].values():
            nameserverName.append(entry['vyos_config_value'])
        # Nameserver addresses
        if '$nameserverAddresses' in entry['mapping'].values():
            nameserverAddresses.append(entry['vyos_config_value'])
        # networkAddresse and networkAddressSpaceStart
        if '$networkAddressSpaceStart' in entry['mapping'].values():
            networkAddress.append(entry['args'][1])
            networkAddressSpaceStart.append(entry['vyos_config_value'])
        # networkAddressSpaceEnd
        if '$networkAddressSpaceEnd' in entry['mapping'].values():
            networkAddressSpaceEnd.append(entry['vyos_config_value'])
        # interface and routerAddress
        if '$interfaceInformation' in entry['mapping'].values():    
            interfaceName.append(entry['args'][0])
            interfaceAddress.append(entry['vyos_config_value'])


    # initialize additional lists
    subnetMask = []
    networkAddressFinal = []
    brAddr = []
    interfaces = []
    rouAddr = []

    # process network information for dhcp configruation
    for network in networkAddress:
        ipv4 = ipaddress.IPv4Network(network)
        networkAddressFinal.append(str(ipv4.network_address))
        subnetMask.append(str(ipv4.netmask))
        brAddr.append(str(ipv4.broadcast_address))

        for interfaceNetwork in interfaceAddress:
            if interfaceNetwork != 'dhcp':
                interfaceipv4 = ipaddress.IPv4Interface(interfaceNetwork)
                if interfaceipv4.network.network_address == ipv4.network_address:
                    rouAddr.append(str(interfaceipv4.ip))
                    interfaces.append(interfaceName[interfaceAddress.index(interfaceNetwork)])

    # make nameserver and addesses unique
    nameserverName = list(set(nameserverName))
    nameserverAddresses = list(set(nameserverAddresses))

    # read DHCP configuration template file
    with open(dhcpTemplate, 'r') as file:
        dhcpConfiguration = file.read()

    # replace variables in DHCP configuration template with values
    if subnetMask:
        dhcpConfiguration = dhcpConfiguration.replace("{$subnetMask}", str(subnetMask[0]))

    if nameserverAddresses:
        representation = str(nameserverAddresses[0])
        for i in range(1, len(nameserverAddresses)):
            representation += ', ' + nameserverAddresses[i]
        dhcpConfiguration = dhcpConfiguration.replace("{$nameserverAddresses}", representation)

    if nameserverName:
        dhcpConfiguration = dhcpConfiguration.replace('{$nameserverName}', nameserverName[0])


    for pos in range(0,len(networkAddress)):
        with open(subnetTemplatePath, 'r') as file:
            subnetTemplate = file.read()

        subnetTemplate = subnetTemplate.replace('{$networkAddress}', networkAddress[pos])
        subnetTemplate = subnetTemplate.replace('{$subnetMask}', subnetMask[pos])
        
        if brAddr[pos]:
            subnetTemplate = subnetTemplate.replace('{$brAddr}', brAddr[pos])

        if rouAddr[pos]:
            subnetTemplate = subnetTemplate.replace('{$rouAddr}', rouAddr[pos])

        if interfaces[pos]:
            subnetTemplate = subnetTemplate.replace('{$interface}', interfaces[pos])

        if networkAddressSpaceStart[pos]:
            subnetTemplate = subnetTemplate.replace('{$networkAddressSpaceStart}', networkAddressSpaceStart[pos])
            subnetTemplate = subnetTemplate.replace('{$networkAddressSpaceEnd}', networkAddressSpaceEnd[pos])
        dhcpConfiguration += subnetTemplate

    # delete all lines with placeholders 
    clearedDhcpConfiguration = remove_subpattern_lines(dhcpConfiguration)

    return clearedDhcpConfiguration


    ### BGP parser

def remove_empty_lines(config):
    lines = config.split("\n")
    result_lines = []
    skip_next_empty_line = False

    for line in lines:
        if line.strip() != "":
            result_lines.append(line)
            skip_next_empty_line = False
        elif not skip_next_empty_line:
            result_lines.append(line)
            skip_next_empty_line = True
            while len(result_lines) > 0 and result_lines[-1].strip() == "":
                result_lines.pop()

    result_config = "\n".join(result_lines)
    return result_config

def vyos_bgp_to_nix_bgp_deamon_config(vyos_config_path : str):
    # NixOS-Template-Pfad
    nixos_template_path = "bgpTemplates/bgptemplate.txt"

    # Lesen der VyOS-Konfiguration aus der Datei
    with open(vyos_config_path) as file:
        vyos_config = json.load(file)

    # BGP-Parameter aus der VyOS-Konfiguration extrahieren. Wenn der Pfad nicht existiert, den Wert auf False
    if "protocols" in vyos_config and "bgp" in vyos_config["protocols"] and "system-as" in vyos_config["protocols"]["bgp"]:
        bgp_as_number = vyos_config.get("protocols", {}).get("bgp", {}).get("system-as", "")
    else:
        bgp_as_number = False 

    if "protocols" in vyos_config and "bgp" in vyos_config["protocols"] and "router-id" in vyos_config["protocols"]["bgp"]["parameters"]:    
        bgp_router_id = vyos_config.get("protocols", {}).get("bgp", {}).get("parameters", {}).get("router-id", "")
    else:
        bgp_router_id = False
    if "protocols" in vyos_config and "bgp" in vyos_config["protocols"] and "address-family" in vyos_config["protocols"]["bgp"] and "ipv4-unicast" in vyos_config["protocols"]["bgp"]["address-family"] and "network" in vyos_config["protocols"]["bgp"]["address-family"]["ipv4-unicast"]:    
        network_address = vyos_config.get("protocols", {}).get("bgp", {}).get("address-family", {}).get("ipv4-unicast", {}).get("network", {}).keys()
    else:
        network_address = False

    if "protocols" in vyos_config and "bgp" in vyos_config["protocols"] and "neighbor" in vyos_config["protocols"]["bgp"]:
        neighbors = vyos_config.get("protocols", {}).get("bgp", {}).get("neighbor", {})
    else:
        neighbors = False    

    # Liste der Nachbarn und ihre Konfiguration
    neighbor_configurations = []
    first_neighbor = True
    # Überprüfung, ob Nachbarn vorhanden sind
    if neighbors:
        for neighbor_ip, neighbor_data in neighbors.items():
            neighbor_as_number = neighbor_data.get("remote-as", "")
            # ebgp_multihop = neighbor_data.get("ebgp-multihop", "")
            # update_source = neighbor_data.get("update-source", "")
            
            # Überprüfung, ob alle erforderlichen Parameter für den Nachbarn vorhanden sind
            if all([neighbor_ip, neighbor_as_number]):
                neighbor_configuration = f"neighbor {neighbor_ip} remote-as {neighbor_as_number}"
                
                # if ebgp_multihop:
                #     neighbor_configuration += f"\nebgp-multihop {ebgp_multihop}"
                
                # if update_source:
                #     neighbor_configuration += f"\nupdate-source {update_source}"

            #richtige formatierung bei nixos
            if first_neighbor: 
                neighbor_configurations.append(neighbor_configuration)
                first_neighbor = False
            else:
                neighbor_configurations.append("    " + neighbor_configuration)


    # Lesen des NixOS-Templates aus der Datei
    with open(nixos_template_path) as file:
        nixos_template = file.read()

    # Platzhalter in NixOS-Vorlage ersetzen
    if bgp_as_number:
        nixos_template = nixos_template.replace("{$bgpAsNumber}", bgp_as_number)
    else:    
        nixos_template = nixos_template.replace("router bgp {$bgpAsNumber}", "\n")    

    if bgp_router_id:    
        nixos_template = nixos_template.replace("{$bgpRouterId}", bgp_router_id)
    else:
        nixos_template = nixos_template.replace("bgp router-id {$bgpRouterId}\n", "\n")    

    if network_address:    
        nixos_template = nixos_template.replace("{$networkAddress}", "\n".join(network_address))
    else:
        nixos_template = nixos_template.replace("network {$networkAddress}\n", "\n")
        

    if neighbor_configurations:
        nixos_template = nixos_template.replace("{$neighborConfigurations}", "\n".join(neighbor_configurations))
    else:
        nixos_template = nixos_template.replace("network {$networkAddress}\n", "\n")    

    clearedNixosTemplate = remove_empty_lines(nixos_template)
    # Ausgabe der NixOS-Konfiguration
    # print(clearedNixosTemplate)
    return clearedNixosTemplate

def create_interface_mapping(vyos_config_path):
    # JSON-Datei einlesen
    with open(vyos_config_path, "r") as f:
        vyos_config = json.load(f)

    vyos_network_config = vyos_config.get("interfaces", {})

    interfaces_vyos = []

    # Ethernet-Interfaces sammeln
    if "ethernet" in vyos_network_config:
        ethernet_interfaces = vyos_network_config["ethernet"]
        interfaces_vyos.extend(list(ethernet_interfaces.keys()))

    # # Loopback-Interfaces sammeln
    # if "loopback" in vyos_network_config:
    #     loopback_interfaces = vyos_network_config["loopback"]
    #     interfaces_vyos.extend(list(loopback_interfaces.keys()))

    # WireGuard-Interfaces sammeln
    if "wireguard" in vyos_network_config:
        wireguard_interfaces = vyos_network_config["wireguard"]
        interfaces_vyos.extend(list(wireguard_interfaces.keys()))

    # Ausführung des Befehls "ip a" und Erfassung der ausgegebenen Interfaces
    command = "ip a"
    output = subprocess.check_output(command, shell=True).decode("utf-8")

    interfaces_nixos = []

    # Verarbeiten der Ausgabe von "ip a" und Erfassen der Interfaces
    lines = output.splitlines()
    for line in lines:
        if line[0].isdigit():
            # Zeile enthält ein Interface
            parts = line.split(":")
            interface = parts[1].strip()
            if not interface.startswith("lo"):  # Loopback interface skippen
                interfaces_nixos.append(interface)
    # Mapping-Dictionary erstellen
    interface_mapping = {}

    # Interfaces abbilden
    for vyos_interface in interfaces_vyos:
        if interfaces_nixos:
            # NixOS-Interface für VyOS-Interface finden und zuordnen
            nixos_interface = interfaces_nixos.pop(0)
            interface_mapping[vyos_interface] = nixos_interface
        else:
            # Keine weiteren NixOS-Interfaces vorhanden, Mapping abbrechen
            break
    
    return interface_mapping

def replace_interface_names(nixos_config, interface_mapping):
    # Replace interface names in NixOS configuration
    for vyos_interface, nixos_interface in interface_mapping.items():
        nixos_config = nixos_config.replace(vyos_interface, nixos_interface)

    return nixos_config
