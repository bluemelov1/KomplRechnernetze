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