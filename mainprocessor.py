import copy
import re
import postprocessor

    
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

# insert extraced values into nix config
def insert_elements(string, elements):
    for i, element in enumerate(elements):
        string = string.replace(f'${i}', element)
    return string


def insert_elements_with_bracks(string, elements):
        # Find the highest placeholder index
    highest_index = -1
    for i in range(len(elements)):
        placeholder = f'${i+1}'
        if placeholder in string:
            highest_index = i+1

    # Enclose each element in the list with "var"
    enclosed_elements = [f'"{element}"' for element in elements]

    # Connect enclosed elements to a list enclosed in curly braces
    connected_elements = f'[{" ".join(enclosed_elements)}]'

    # Replace the highest placeholder with the connected elements
    string = string.replace(f'${highest_index}', connected_elements)
    return string

# convert string to final nix config
def convert_string(string):
    # Use regular expressions to find placeholders and values within curly braces
    pattern = r'{([^}]+)}'
    matches = re.findall(pattern, string)

    # Replace placeholders with corresponding values
    for match in matches:
        placeholder = f'{{{match}}}'
        value = f'{match.strip()}'
        string = string.replace(placeholder, value)
    return string

# convert string to final nix config without ""
def convert_string_with_brack(string):
    # Use regular expressions to find placeholders and values within curly braces
    pattern = r'{([^}]+)}'
    matches = re.findall(pattern, string)

    # Replace placeholders with corresponding values
    for match in matches:
        placeholder = f'{{{match}}}'
        value = f'{match.strip()};'
        string = string.replace(placeholder, value)
    return string

# convert list of lists to list with all subelements
def convert_list_syntax(input_list):
    output_list = []
    
    for sublist in input_list:
        output_list.extend(sublist)
    
    return [output_list]

# combine lists with same first elements to [[pathvar1, pathvar2, ...], value1, value2, ...]
def combine_lists(lists):
    combined = []
    for lst in lists:
        found = False
        for combined_lst in combined:
            if lst[:-1] == combined_lst[0]:
                combined_lst.append(lst[-1])
                found = True
                break
        if not found:
            combined.append([lst[:-1], lst[-1]])
    return combined

# check if keyword list is prefix of one of the vyos paths (lists with keywords)
def check_prefix(keyword_list, data_structure):
    for item in data_structure:
        if item[:len(keyword_list)] == keyword_list:
            return True
    return False


def extract_dollars(vyos_config, mappings, vyos_config_path):
    # make vyos_config representation to list of list
    vyos_config_list = []
    # nix config strings
    nixos_config_start = (
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
    translated_nix_config = [
        nixos_config_start
        ]
    
    #preprocessor.print_decoded_config(vyos_config)
    #preprocessor.print_mapping(mappings)
    #print(mappings)

    # split vyos config into list of sections
    for line in vyos_config:
        line = line.replace('=', '#').split("#")
        # print(line)
        vyos_config_list.append(line)
    
    # print(vyos_config_list)


    # go trough all mapping entries
    for mapping in mappings:
        # list for all dollar signes to save to
        dollars = []
        # list for all required matches
        requirements = mapping.split(";")
        #print(requirements)
        # divide the requirement string into sections
        for num, req in enumerate(requirements):
            req = req.replace('=', '#').split("#")
            #print(req)
            # compare vyos_config_list of lists with requirements list
            for config_line in vyos_config_list:
                req_temp = req
                dollars_temp = []
                while config_line[0] == req_temp[0] or req_temp[0][0] == "$" or req_temp[0].startswith('^'):
                    #print(config_line)
                    #print(req_temp)
                    #print(req_temp[0][0])
                    # case of value extraction
                    if req_temp[0][0] == "$":
                        dollars_temp.append(config_line[0])
                        config_line = config_line[1:]
                        req_temp = req_temp[1:]
                        if len(config_line) < 1:
                            dollars.append(dollars_temp)
                        if len(config_line) < 1 or len(req_temp) < 1:
                            break
                        continue
                    #print(len(config_line))
                    #print(len(req_temp))
                    # case of regular expression
                    if req_temp[0].startswith('^'):
                        matches = re.match(req_temp[0], config_line[0])
                        #print(matches)
                        # TODO maybe group(0) should not be added
                        if matches:
                            for match in matches.groups():
                                dollars_temp.append(match)    

                            config_line = config_line[1:]
                            req_temp = req_temp[1:]
                            if len(config_line) < 1:
                                dollars.append(dollars_temp)
                            if len(config_line) < 1 or len(req_temp) < 1:
                                break
                            continue
                        else:
                            break

                    if len(config_line) == 1 or len(req_temp) == 1:
                        break
                    config_line = config_line[1:]
                    req_temp = req_temp[1:]
                    #print(config_line)
                    #print(req_temp)
            if num > 0 and len(dollars) > 0:
                dollars = convert_list_syntax(dollars)
            #print(dollars)


        # just one mapping found then translate and append to nix config
        if len(dollars) == 1:
            # get translated nix mapping template
            nix_mappping = mappings[mapping]
            #print(nix_mappping)
            inserted_elements = insert_elements(nix_mappping, dollars[0])
            #print(inserted_elements)
            #result = convert_string(inserted_elements)
            #print(result)
            translated_nix_config.append(inserted_elements)
    
        # multiple mappings found then translate and append to nix config
        elif len(dollars) > 1:
            nix_mappping = mappings[mapping]
            #print(nix_mappping)
            path_var_split = combine_lists(dollars)
            #print(path_var_split)
            for path in path_var_split:
                inserted_elements = insert_elements(nix_mappping, path[0])
                #print(inserted_elements)
                path = path[1:]
                #print(path)
                inserted_elements = insert_elements_with_bracks(inserted_elements, path)
                #print(result)
                translated_nix_config.append(inserted_elements)
            

    if check_prefix(['service', 'dhcp-server'], vyos_config_list):
        translated_nix_config.append(postprocessor.get_dhcp_configuration(vyos_config))

    if check_prefix(['protocols', 'bgp'], vyos_config_list):
        translated_nix_config.append(postprocessor.vyos_bgp_to_nix_bgp_deamon_config(vyos_config_path))

        #print(mapping)
        #print(dollars)

    config_nixos_end = (
        f'  environment.systemPackages = with pkgs; [\n'    
        f'    vim\n'    
        f'    frr\n'    
        f'  ];\n'    
        f'  system.stateVersion = "22.11;"\n'    
        f'}}'    
    )
    

    translated_nix_config.append(config_nixos_end)

    return translated_nix_config

