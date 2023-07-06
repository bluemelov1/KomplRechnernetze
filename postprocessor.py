import copy
import ipaddress
import re

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