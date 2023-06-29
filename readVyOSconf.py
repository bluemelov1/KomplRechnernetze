import json

#path='szenario1/vyos/bonding/config.json'
path='szenario2/vyos/config-client.json'

def generate_entry_strings(data, prefix=''):
    entries = []

    if isinstance(data, dict):
        for key, value in data.items():
            entry = f"{prefix}{key}"  # Aktuelle Schlüsselzeichenkette

            if isinstance(value, dict) or isinstance(value, list):
                sub_entries = generate_entry_strings(value, prefix=f"{entry}#")  # Generiere rekursiv Untereinträge für dict oder list
                entries.extend(sub_entries)
            else:
                entries.append(f"{entry}:{value}")  # Füge die aktuelle Schlüsselzeichenkette mit Wert hinzu

    elif isinstance(data, list):
        for item in data:
            entry = f"{prefix}"  # Aktuelle Schlüsselzeichenkette
            entries.append(f"{entry}:{item}")
            
    return entries

# Lese die JSON-Datei ein
with open(path) as file:
    json_data = json.load(file)

# Generiere Array von Eintragszeichenketten mit inneren Werten
entries = generate_entry_strings(json_data)


# Gebe das Array aus
for entry in entries:
    print(entry)
print(len(entries))