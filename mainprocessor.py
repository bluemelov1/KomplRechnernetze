import copy
import re

    
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

def parseToNixConfig(checking_result_data : list):
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

    nixos_config = (
        f'{{ config, pkgs, ...}}\n'
        f'{{\n'
        f'  imports =\n'
        f'    [\n'
        f'      ./hardware-configuration.nix\n'
        f'    ];\n'
        f'  boot.loader.grub.enable = true;\n'
        f'  boot.loader.grub.version = 2;\n'
        f'  boot.loader.grub.device = "/dev/sda";\n'
    )
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
                # if regex
                else:
                    regex = vyos_sep[1]
                    regex_nix_args_extention = nixos_sep[1].split(";")
                    matches = re.match(regex, group_mapping_entry["values"][0])

                    if matches:
                        nixos_config += f'  {vyos_path_to_nixos_path(nixos_sep[0], group_mapping_entry["args"])} = ' + '{' + f'\n'
                        for i in range(len(regex_nix_args_extention)-1):
                            nixos_config += f'    {regex_nix_args_extention[i]} = "{matches.group(i)}";\n'
                        nixos_config += "  };" + f'\n'

            # multiple values --> need []
            else:
                # if no regex
                if len(vyos_sep) == 1 and len(nixos_sep) == 1:
                    nixos_config += f'  {vyos_path_to_nixos_path(nixos_sep[0], group_mapping_entry["args"])} = ['
                    for value in group_mapping_entry["values"]:
                        nixos_config += f'  "{value}", '
                    nixos_config = nixos_config[:-2]
                    nixos_config += "  ];\n"
                # if regex
                else:
                    regex = vyos_sep[1]
                    regex_nix_args_extention = nixos_sep[1].split(";")
                    # matches = re.match(regex, group_mapping_entry["values"][0])

                    nixos_config += f'  {vyos_path_to_nixos_path(nixos_sep[0], group_mapping_entry["args"])} = [\n'
                    for value in group_mapping_entry["values"]:
                        matches = re.match(regex, value)
                        if matches:
                            print("Group1", matches.group(1))
                            print("Group2", matches.group(2))
                            nixos_config += '    {' + f'\n'
                            for i in range(1, len(regex_nix_args_extention)+1):
                                print("*****************", i)
                                nixos_config += f'      {regex_nix_args_extention[i-1]} = "{matches.group(i)}";\n'
                                print("#+#+#+", regex_nix_args_extention[i-1])
                                print("#+#+#+", matches.group(i))
                            nixos_config += "    }," + f'\n'
                    nixos_config = nixos_config[:-2]
                    nixos_config += f'\n'
                    nixos_config += f'  ];\n'
    nixos_config += (
        f'  environment.systemPackages = with pkgs; [\n'    
        f'    vim\n'    
        f'  ];\n'    
        f'  system.stateVersion = "22.11;"\n'    
        f'}}'    
    )
    return nixos_config

