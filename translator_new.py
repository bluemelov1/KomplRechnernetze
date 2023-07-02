import copy
import sys
import json
import re

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

def vyos_path_to_nixos_path(nixos_config_path : str, args : dict):
    nixos_keywords = nixos_config_path.split("#")
    print("+++++", nixos_keywords)
    nixos_result = ""
    for keyword in nixos_keywords:
        if keyword[0] == "$":
            arg_id = int(keyword[1:])
            print(args)
            print(arg_id)
            nixos_result += args.get(arg_id) + "."
        else:
            nixos_result += keyword + "."
    return nixos_result[:-1]

def parseToNixConfig1(checking_result_data : list):
    print(checking_result_data) 
    group_mapping = []
    # go through checking result data (mapping, args, vyos_config_value)
    for result_data_entry in checking_result_data:
        group_mapping_iter = copy.deepcopy(group_mapping)
        a = False
        # check if mapping already in group_mapping list
        for i in range(len(group_mapping_iter)):
            if group_mapping[i]["mapping"] == result_data_entry["mapping"]:
                # mapping already in group_mapping --> append value to values
                group_mapping[i]["values"].append(result_data_entry["vyos_config_value"])
                a = True
        # if not in mapping add new entry to group_mapping
        if not a:
            group_mapping.append({
                "mapping": result_data_entry["mapping"],
                "args": result_data_entry["args"],
                "values" : [result_data_entry["vyos_config_value"]]
                })
    print("Group mapping", group_mapping)

    nixos_config = ""
    # translate to nix config
    for group_mapping_entry in group_mapping:
        for vyos_config_path, nixos_config_path in group_mapping_entry["mapping"].items():
            vyos_sep = vyos_config_path.split("~")
            nixos_sep = nixos_config_path.split("~")

            # no multiple values
            if len(group_mapping_entry["values"]) == 1:
                # if no regex
                if len(vyos_sep) == 1 and len(nixos_sep) == 1:
                    nixos_config += f'{vyos_path_to_nixos_path(nixos_sep[0], group_mapping_entry["args"])} = "{group_mapping_entry["values"][0]}";\n'
                    print(nixos_config)
                # if regex
                else:
                    regex = vyos_sep[1]
                    regex_nix_args_extention = nixos_sep[1].split(";")
                    matches = re.match(regex, group_mapping_entry["values"][0])

                    if matches:
                        nixos_config += f'{vyos_path_to_nixos_path(nixos_sep[0], group_mapping_entry["args"])} = ' + '{' + f'\n'
                        for i in range(len(regex_nix_args_extention)-1):
                            nixos_config += f'  {regex_nix_args_extention[i]} = "{matches.group(i)}";\n'
                        nixos_config += "};" + f'\n'

            # multiple values --> need []
            else:
                # if no regex
                if len(vyos_sep) == 1 and len(nixos_sep) == 1:
                    nixos_config += f'{vyos_path_to_nixos_path(nixos_sep[0], group_mapping_entry["args"])} = ['
                    for value in group_mapping_entry["values"]:
                        nixos_config += f'"{value}", '
                    nixos_config = nixos_config[:-2]
                    nixos_config += "];\n"
                # if regex
                else:
                    regex = vyos_sep[1]
                    regex_nix_args_extention = nixos_sep[1].split(";")
                    # matches = re.match(regex, group_mapping_entry["values"][0])

                    nixos_config += f'{vyos_path_to_nixos_path(nixos_sep[0], group_mapping_entry["args"])} = [\n'
                    for value in group_mapping_entry["values"]:
                        matches = re.match(regex, value)
                        if matches:
                            print("Group1", matches.group(1))
                            print("Group2", matches.group(2))
                            nixos_config += '{' + f'\n'
                            for i in range(1, len(regex_nix_args_extention)+1):
                                print("*****************", i)
                                nixos_config += f'  {regex_nix_args_extention[i-1]} = "{matches.group(i)}";\n'
                                print("#+#+#+", regex_nix_args_extention[i-1])
                                print("#+#+#+", matches.group(i))
                            nixos_config += "}," + f'\n'
                    nixos_config = nixos_config[:-2]
                    nixos_config += f'\n'
                    nixos_config += f'];\n'

            # ip_regex = r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d{1,2})$'

                
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
    # 'interfaces#bonding#$0#hash-policy' : '0#E0#$0',
    'interfaces#bonding#$0#address~^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d{1,2})$': 'test#$0#test~adress;prefixLength',
    # 'interfaces#bonding#$0#member#interface': '0#E0#$0',
    # 'interfaces#bonding#$0#mode': '2#3#E1#4',
    # 'interfaces#ethernet#$0#hw-id': '1#$0#E2#5#$1',
    # 'interfaces#ethernet#$0#address': '1#$0#E2#5#$1',
    # 'service#ntp#allow-client#address': '1#$0#E2#5#$1',
    # 'system#config-management#commit-revisions': '1#$0#E2#5#$1',
    # 'system#console#device#ttyS0#speed': '1#$0#E2#5#$1',
    'system#host-name': 'networking#hostName',
    # 'system#login#user#vyos#authentication#encrypted-password': '1#$0#E2#5#$1',
    # 'system#login#user#vyos#authentication#plaintext-password': '1#$0#E2#5#$1',
    # 'system#syslog#global#facility#all#level': '1#$0#E2#5#$1',
    # 'system#syslog#global#facility#local7#level': '1#$0#E2#5#$1'
    }

# Gebe das Array aus
for entry in vyos_config:
    print(entry)
print(len(vyos_config))

checking_result_data = []

for vyos_config_path in vyos_config:
    vyos_config_sep = vyos_config_path.split("=")
    vyos_config_keywords = vyos_config_sep[0].split("#")

    mapping_hit = copy.deepcopy(mapping)
    args = {}

    checking_hit = check(vyos_config_keywords, mapping_hit, args, 0)

    if checking_hit:
        checking_result_data.append({
            "mapping" : mapping_hit,
            "args" : args,
            "vyos_config_value" : vyos_config_sep[1]
        })
        print(f"\nVyos Config Path: " + vyos_config_path)
        print("Config Value: ", vyos_config_sep[1])
        print("Mapping Hit: ", checking_hit)
        print("Mapping entry: ", mapping_hit)
        print("Extracted Args: ", args)
    
parseToNixConfig1(checking_result_data)
    

    # for vyos_config_path, nixos_config_path in mapping_hit.items():
    #     print(parseToNixConfig(vyos_config_path, nixos_config_path, args))



