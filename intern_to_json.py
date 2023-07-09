import re
import json
import sys

def process_mapping_line(mapping, mapping_line):
    vyos_part, nixos_full_path = mapping_line.split('@')
    vyos_full_paths = vyos_part.split(';')
    print(vyos_full_paths)
    for vyos_full_path in vyos_full_paths:
        vyos_path, vyos_value = vyos_full_path.split('=')
        print("Vyos_path: " + vyos_path + " Vyos_value: " + vyos_value)
        vyos_path_keywords = vyos_path.split('#')
        current_mapping = mapping
        for vyos_keyword in vyos_path_keywords:
            if vyos_keyword.startswith('$'):
                if vyos_keyword not in current_mapping:
                    current_mapping[vyos_keyword] = {}
                current_mapping = current_mapping[vyos_keyword]
            else:
                if vyos_keyword not in current_mapping:
                    current_mapping[vyos_keyword] = {}
                current_mapping = current_mapping[vyos_keyword]
        current_mapping["vyosValue"] = vyos_value
        current_mapping["nixosPath"] = nixos_full_path


def convert_mapping_to_json(mapping):
    return json.dumps(mapping, indent=2)

def main():
    # if len(sys.argv) < 2:
    #    print("Bitte geben Sie den Pfad zur Mapping-Datei als Befehlszeilenargument an.")
    #    return

    # mapping_file = sys.argv[1]
    mapping_file = "mappings/wireguardMapping.txt"
    mapping = {}

    try:
        with open(mapping_file, 'r') as file:
            for line in file:
                mapping_line = line.strip()
                if mapping_line:
                    process_mapping_line(mapping, mapping_line)

        json_output = convert_mapping_to_json(mapping)
        print(json_output)

    except FileNotFoundError:
        print("Die angegebene Mapping-Datei wurde nicht gefunden.")
    except Exception as e:
        print("Ein Fehler ist aufgetreten:", str(e))

if __name__ == "__main__":
    main()

