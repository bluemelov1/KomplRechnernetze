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

def get_vyos_config( path):
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