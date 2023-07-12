import json
import os

    
#### import vyos json config

def generate_entry_strings(data, prefix=''):
    
    entries = []

    # if vyos config end with {}
    '''
    Example:

    "protocols": {
        "static": {
            "route": {
                "0.0.0.0/0": {
                    "next-hop": {
                        "192.168.111.1": {}
                    }
                }
            }
        }
    },
    '''
    if isinstance(data, dict) and len(data) == 0:
        entries.append(f'{prefix[:-1]}={{}}')
    elif isinstance(data, dict):
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

def get_vyos_config(path):
    # read JSON file
    with open(path) as file:
        json_data = json.load(file)

    return generate_entry_strings(json_data)

def print_decoded_config( config):
    for entry in config:
        print(entry)
    print(len(config))

#### import mapping files 

# Read all file names of a folder
def read_files_in_folder( folder_path, filenames):
    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        # Construct the full file path
        file_path = os.path.join(folder_path, file_name)
        
        # Check if the path points to a file
        if os.path.isfile(file_path):
            # Add the filenames to list
            filenames.append(file_name)
            # Print the file name
            # print(file_name)

# Save mapping file as dictionary
def read_file_and_save_mapping( file_path, dict_to_save_to):

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()

        if '@' in line:
            key, value = line.split('@', 1)
            dict_to_save_to[key] = value

def get_mapping_as_dict( folder_path):
    files = []
    read_files_in_folder(folder_path, files)
    # Specify the output file path
    mapping = {}
    # Call the function to read the file and save the mapping

    for file_path in files:
        read_file_and_save_mapping(folder_path + '/' + file_path, mapping)

    return mapping

def print_mapping(dictionary):
    for key, value in dictionary.items():
        print(f"'{key}': '{value}'")


# Function to traverse a JSON object
def traverse_json(json_obj, dict_to_save, path=""):
    if isinstance(json_obj, dict):  # If the JSON object is a dictionary
        for k, v in json_obj.items():  # Iterate over each key-value pair
            new_path = path + "#" + k if path else k  # Append the current key to the path
            if isinstance(v, dict):  # If the value is another dictionary
                traverse_json(v, dict_to_save, new_path)  # Recursively traverse the nested dictionary
            elif k == "nixosPath":  # If the key is "nixosPath"
                vyos_path = json_obj.get("additionalVyOSPath", [""])[0]  # Get the value of "additionalVyOSPath" and replace "$" with "="
                vyos_value = json_obj.get("vyosValue", "")  # Get the value of "vyosValue" and replace "$" with "="
                #path = replace_last_occurrence(path, "#", "")  # Remove the last occurrence of "#"
                
                vyos_req = ""
                nixos_path = ""
                if vyos_path:
                    #print(f"{path}={vyos_value};{vyos_path}@{v};")  # Print the formatted output
                    vyos_req = f"{path}={vyos_value};{vyos_path}"
                else:
                    #print(f"{path}={vyos_value}@{v};")
                    vyos_req = f"{path}={vyos_value}"
                nixos_path = v + ";"
                
                if vyos_req:
                    #print(f"vyos_req: {vyos_req}")
                    dict_to_save[vyos_req] = nixos_path
    elif isinstance(json_obj, list):  # If the JSON object is a list
        for i in json_obj:  # Iterate over each element in the list
            traverse_json(i, dict_to_save, path)  # Recursively traverse the list element


# get internal mapping syntax from JSON
def get_internal_mapping_syntax(path):
    with open(path) as json_file:
        json_obj = json.load(json_file)

    dict_with_mapping = {}
    # Traverse the JSON object
    traverse_json(json_obj, dict_with_mapping)
    #print_mapping(dict_with_mapping)
    return dict_with_mapping

