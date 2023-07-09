import copy
import re 

import preprocessor
import mainprocessor
import postprocessor

#VyOS_path = "szenario1/vyos/bonding/config.json"
#VyOS_path = "szenario1/vyos/dhcp/dhcp-server.json"
#VyOS_path = "szenario1/vyos/dhcp/dhcp-client.json"
#VyOS_path = "szenario2/vyos/config-server.json"
VyOS_path = "szenario3/vyos/client_0/config.json"

vyos_config = preprocessor.get_vyos_config(VyOS_path)


mappings = preprocessor.get_mapping_as_dict('mappings')

# preprocessor.print_mapping(mappings)

'''
Theorie:

- Einlesen des mappings
- aufteilen eingabe ausgabe
- aufteilen eingabe falls nötig
- (aufteilen ausgabe falls nötig)

    - suche von match für alle eingaben, speichern der $x und überprüfen der Regeln
'''

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
    connected_elements = f'[{", ".join(enclosed_elements)}]'

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


def extract_dollars(vyos_config, mappings):
    # make vyos_config representation to list of list
    vyos_config_list = []
    # nix config strings
    translated_nix_config = []
    
    #preprocessor.print_decoded_config(vyos_config)
    #preprocessor.print_mapping(mappings)
    #print(mappings)

    # split vyos config into list of sections
    for line in vyos_config:
        line = line.replace('=', '#').split("#")
        # print(line)
        vyos_config_list.append(line)

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
                #print(inserted_elements)
                result = convert_string_with_brack(inserted_elements)
                #print(result)
                translated_nix_config.append(result)
            

        #print(mapping)
        #print(dollars)
    for i in translated_nix_config:
        print(i)

    #print(translated_nix_config)    




extract_dollars(vyos_config, mappings)
