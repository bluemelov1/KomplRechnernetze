import copy
import sys
import json

def generate_entry_strings(data, prefix=''):
    entries = []

    if isinstance(data, dict):
        for key, value in data.items():
            entry = f"{prefix}{key}"  # Aktuelle Schlüsselzeichenkette

            if isinstance(value, dict):
                sub_entries = generate_entry_strings(value, prefix=f"{entry}#")  # Generiere rekursiv Untereinträge für dict oder list
                entries.extend(sub_entries)
            elif isinstance(value, list):
                sub_entries = generate_entry_strings(value, prefix=f"{entry}")  # Generiere rekursiv Untereinträge für dict oder list
                entries.extend(sub_entries)
            else:
                entries.append(f"{entry}={value}")  # Füge die aktuelle Schlüsselzeichenkette mit Wert hinzu

    elif isinstance(data, list):
        for item in data:
            entry = f"{prefix}"  # Aktuelle Schlüsselzeichenkette
            entries.append(f"{entry}={item}")
            
    return entries

def check(vyos_config_keywords : list, mapping : dict, args : list, depth : int):
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
        # get vyos keywords from mapping entry
        vyos_mapping_keywords = vyos_mapping_path.split("#")
        # print(vyos_config_keywords[0] + " // " + vyos_mapping_keywords[depth])
        # check if keyword begins with "$" -> identifier
        if vyos_mapping_keywords[depth][0] == "$":
            # append arg from vyos config -> $[indexOfArray]
            args.append(vyos_config_keywords[0])
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


            
                
'''
DEMO

vyos_config = ['0#a#2=\"test\"', '2#3#4=\"test\"', '1#b#5#c=\"test\"', '8#4#3#2=\"test\"']

mapping = {
    '0#$0#2': '0#E0#$0',
    '2#3#4': '2#3#E1#4',
    '1#$0#5#$1': '1#$0#E2#5#$1',
    }

for vyos_config_path in vyos_config:
    vyos_config_sep = vyos_config_path.split("=")
    vyos_config_keywords = vyos_config_sep[0].split("#")

    mapping_hit = copy.deepcopy(mapping)
    args = []

    print(check(vyos_config_keywords, mapping_hit, args, 0))

'''

# path = sys.argv[1]
path = "szenario1/vyos/bonding/config.json"

# Lese die JSON-Datei ein
with open(path) as file:
    json_data = json.load(file)

# Generiere Array von Eintragszeichenketten mit inneren Werten
vyos_config = generate_entry_strings(json_data)

mapping = {
    'interfaces#bonding#bond0#hash-policy' : '0#E0#$0',
    'interfaces#bonding#bond0#address': '0#E0#$0',
    'interfaces#bonding#$0#member#interface': '0#E0#$0',
    'interfaces#bonding#$0#mode': '2#3#E1#4',
    'interfaces#ethernet#$0#hw-id': '1#$0#E2#5#$1',
    'interfaces#ethernet#$0#address': '1#$0#E2#5#$1',
    'service#ntp#allow-client#address': '1#$0#E2#5#$1',
    'system#config-management#commit-revisions': '1#$0#E2#5#$1',
    'system#console#device#ttyS0#speed': '1#$0#E2#5#$1',
    'system#host-name': '1#$0#E2#5#$1',
    'system#login#user#vyos#authentication#encrypted-password': '1#$0#E2#5#$1',
    'system#login#user#vyos#authentication#plaintext-password': '1#$0#E2#5#$1',
    'system#syslog#global#facility#all#level': '1#$0#E2#5#$1',
    'system#syslog#global#facility#local7#level': '1#$0#E2#5#$1'
    }

# Gebe das Array aus
for entry in vyos_config:
    print(entry)
print(len(vyos_config))

for vyos_config_path in vyos_config:
    vyos_config_sep = vyos_config_path.split("=")
    vyos_config_keywords = vyos_config_sep[0].split("#")

    mapping_hit = copy.deepcopy(mapping)
    args = []

    print(f"\nVyos Config Path: " + vyos_config_path)
    print("Mapping Hit: ", check(vyos_config_keywords, mapping_hit, args, 0))
    print("Mapping entry: ", mapping_hit)
    print("Extracted Args: ", args)



