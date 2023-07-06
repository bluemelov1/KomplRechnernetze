import os

# Read all file names of a folder
def read_files_in_folder(folder_path, filenames):
    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        # Construct the full file path
        file_path = os.path.join(folder_path, file_name)
        
        # Check if the path points to a file
        if os.path.isfile(file_path):
            # Add the filenames to list
            filenames.append(file_name)
            # Print the file name
            print(file_name)

# Save mapping file as dictionary
def read_file_and_save_mapping(file_path, dict_to_save_to):

    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()

        if ':' in line:
            key, value = line.split(':', 1)
            dict_to_save_to[key] = value


# Specify the folder path
folder_path = 'mappings'

# Initialize list for filenames
files = []

# Call the function to read files in the folder
read_files_in_folder(folder_path, files)


# Specify the output file path
mapping = {}

# Call the function to read the file and save the mapping
for file_path in files:
    read_file_and_save_mapping(folder_path + '/' + file_path, mapping)

# Print the mapping
print(mapping)