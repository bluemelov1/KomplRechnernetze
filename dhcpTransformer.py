import json
import copy
import ipaddress
import re


def generate_entry_strings(data, prefix=''):
    entries = []

    if isinstance(data, dict):
        for key, value in data.items():
            entry = f"{prefix}{key}"  # current key string 

            if isinstance(value, dict):
                sub_entries = generate_entry_strings(value, prefix=f"{entry}#")  # generate recursive subentries
                entries.extend(sub_entries)
            elif isinstance(value, list):
                sub_entries = generate_entry_strings(value, prefix=f"{entry}")  # generate recursive subentries
                entries.extend(sub_entries)
            else:
                entries.append(f"{entry}={value}")  # add current key string with value

    elif isinstance(data, list):
        for item in data:
            entry = f"{prefix}"  # current key string 
            entries.append(f"{entry}={item}")
            
    return entries

def check(vyos_config_keywords : list, mapping : dict, args : dict, depth : int):
    # break condition: len(mapping) = 0 -> no match
    if len(mapping) == 0:
        return False
    # break condition: all keywords checked and len(mapping) != 0 -> match
    if len(vyos_config_keywords) == 0:
        # print(mapping)
        # print(args)
        return True
    # deep copy because mapping variable is changing in loop (del mapping...): iter_mapping hold state / mapping -> mapping_hit change
    iter_mapping = copy.deepcopy(mapping)
    # iterate through all mapping entries
    for vyos_mapping_path, nixos_mapping_path in iter_mapping.items():
        vyos_mapping_sep = vyos_mapping_path.split("~")
        # get vyos keywords from mapping entry
        vyos_mapping_keywords = vyos_mapping_sep[0].split("#")
        # print(vyos_config_keywords[0] + " // " + vyos_mapping_keywords[depth])
        # check if keyword begins with "$" -> identifier
        if vyos_mapping_keywords[depth][0] == "$":
            # append arg from vyos config -> $[indexOfArray]
            arg_id = int(vyos_mapping_keywords[depth][1:])
            args[arg_id] = vyos_config_keywords[0]
            break
        # check if keyword != keyword on stage "depth" in the config path
        elif vyos_config_keywords[0] != vyos_mapping_keywords[depth]:
            # delete entry because does not match vyos config path
            del mapping[vyos_mapping_path]
        # print(mapping)
        # print(args)
    # delete first entry of vyos config keywords -> finished check for this keyword
    vyos_config_keywords.pop(0)
    # increment depth -> go to next stage in config path
    depth += 1
    return check(vyos_config_keywords, mapping, args, depth)

# remove not found entries in configuration
def remove_subpattern_lines(input_string):
    lines = input_string.split("\n")
    result_lines = []
    for line in lines:
        if not re.search(r'\{\$.*?\}', line):
            result_lines.append(line)
    result_string = "\n".join(result_lines)
    return result_string

# define file paths
vyos_vonfig_path = "szenario1/vyos/dhcp/dhcp-server.json"
dhcpTemplate = 'dhcpTemplates/dhcpTemplate.txt' 
subnetTemplatePath = 'dhcpTemplates/dhcpSubnetTemplate.txt'


# read vyos json
with open(vyos_vonfig_path) as file:
    json_vyos = json.load(file)

# generate our data representation of vyos data
vyos_config = generate_entry_strings(json_vyos)

# print array
for entry in vyos_config:
    print(entry)


dhcpInformationMapping = {
    'service#dhcp-server#shared-network-name#$0#subnet#$1#domain-name' : '$nameserverName',
    'service#dhcp-server#shared-network-name#$0#subnet#$1#name-server' : '$nameserverAddresses',
    'service#dhcp-server#shared-network-name#$0#subnet#$1#range#$2#stop' : '$networkAddressSpaceEnd',
    'service#dhcp-server#shared-network-name#$0#subnet#$1#range#$2#start' : '$networkAddressSpaceStart',
    'interfaces#ethernet#$0#address' : '$interfaceInformation',

}

# list to store data
dhcpExtractedData = []

# iterate through VyOS config entries and check against the mapping
for vyos_config_path in vyos_config:
    vyos_config_sep = vyos_config_path.split("=")
    vyos_config_keywords = vyos_config_sep[0].split("#")

    mapping_hit = copy.deepcopy(dhcpInformationMapping)
    args = {}

    checking_hit = check(vyos_config_keywords, mapping_hit, args, 0)

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


print(dhcpConfiguration)
# delete all lines with placeholders 
clearedDhcpConfiguration = remove_subpattern_lines(dhcpConfiguration)
print(clearedDhcpConfiguration)

