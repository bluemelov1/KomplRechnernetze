import json


# Function to traverse a JSON object
def traverse_json(json_obj, path=""):
    if isinstance(json_obj, dict):  # If the JSON object is a dictionary
        for k, v in json_obj.items():  # Iterate over each key-value pair
            new_path = path + "#" + k if path else k  # Append the current key to the path
            if isinstance(v, dict):  # If the value is another dictionary
                traverse_json(v, new_path)  # Recursively traverse the nested dictionary
            elif k == "nixosPath":  # If the key is "nixosPath"
                vyos_path = json_obj.get("additionalVyOSPath", [""])[0]  # Get the value of "additionalVyOSPath" and replace "$" with "="
                vyos_value = json_obj.get("vyosValue", "")  # Get the value of "vyosValue" and replace "$" with "="
                #path = replace_last_occurrence(path, "#", "")  # Remove the last occurrence of "#"
                if vyos_path:
                    print(f"{path}={vyos_value};{vyos_path}@{v};")  # Print the formatted output
                else:
                    print(f"{path}={vyos_value}@{v};")
    elif isinstance(json_obj, list):  # If the JSON object is a list
        for i in json_obj:  # Iterate over each element in the list
            traverse_json(i, path)  # Recursively traverse the list element

# Load JSON from a file or a string
path = 'output.json'
with open(path) as json_file:
    json_obj = json.load(json_file)

# Traverse the JSON object
traverse_json(json_obj)
