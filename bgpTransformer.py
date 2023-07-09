import json

# VyOS-Konfigurationspfad
vyos_config_path = "szenario3/vyos/bgp_router_0/config.json"

# NixOS-Template-Pfad
nixos_template_path = "bgpTemplates/bgptemplate.txt"

# Lesen der VyOS-Konfiguration aus der Datei
with open(vyos_config_path) as file:
    vyos_config = json.load(file)

# BGP-Parameter aus der VyOS-Konfiguration extrahieren. Wenn der Pfad nicht existiert, den Wert auf False
if "protocols" in vyos_config and "bgp" in vyos_config["protocols"] and "system-as" in vyos_config["protocols"]["bgp"]:
    bgp_as_number = vyos_config.get("protocols", {}).get("bgp", {}).get("system-as", "")
else:
    bgp_as_number = False 

if "protocols" in vyos_config and "bgp" in vyos_config["protocols"] and "router-id" in vyos_config["protocols"]["bgp"]["parameters"]:    
    bgp_router_id = vyos_config.get("protocols", {}).get("bgp", {}).get("parameters", {}).get("router-id", "")
else:
    bgp_router_id = False
if "protocols" in vyos_config and "bgp" in vyos_config["protocols"] and "address-family" in vyos_config["protocols"]["bgp"] and "ipv4-unicast" in vyos_config["protocols"]["bgp"]["address-family"] and "network" in vyos_config["protocols"]["bgp"]["address-family"]["ipv4-unicast"]:    
    network_address = vyos_config.get("protocols", {}).get("bgp", {}).get("address-family", {}).get("ipv4-unicast", {}).get("network", {}).keys()
else:
    network_address = False

if "protocols" in vyos_config and "bgp" in vyos_config["protocols"] and "neighbor" in vyos_config["protocols"]["bgp"]:
    neighbors = vyos_config.get("protocols", {}).get("bgp", {}).get("neighbor", {})
else:
    neighbors = False    

# Liste der Nachbarn und ihre Konfiguration
neighbor_configurations = []
first_neighbor = True
# Überprüfung, ob Nachbarn vorhanden sind
if neighbors:
    for neighbor_ip, neighbor_data in neighbors.items():
        neighbor_as_number = neighbor_data.get("remote-as", "")
        # ebgp_multihop = neighbor_data.get("ebgp-multihop", "")
        # update_source = neighbor_data.get("update-source", "")
        
        # Überprüfung, ob alle erforderlichen Parameter für den Nachbarn vorhanden sind
        if all([neighbor_ip, neighbor_as_number]):
            neighbor_configuration = f"neighbor {neighbor_ip} remote-as {neighbor_as_number}"
            
            # if ebgp_multihop:
            #     neighbor_configuration += f"\nebgp-multihop {ebgp_multihop}"
            
            # if update_source:
            #     neighbor_configuration += f"\nupdate-source {update_source}"

        #richtige formatierung bei nixos
        if first_neighbor: 
            neighbor_configurations.append(neighbor_configuration)
            first_neighbor = False
        else:
            neighbor_configurations.append("    " + neighbor_configuration)


# Lesen des NixOS-Templates aus der Datei
with open(nixos_template_path) as file:
    nixos_template = file.read()

# Platzhalter in NixOS-Vorlage ersetzen
if bgp_as_number:
    nixos_config = nixos_template.replace("{$bgpAsNumber}", bgp_as_number)
else:    
    nixos_config = nixos_template.replace("router bgp {$bgpAsNumber}n", "\n")    

if bgp_router_id:    
    nixos_config = nixos_config.replace("{$bgpRouterId}", bgp_router_id)
else:
    nixos_config = nixos_config.replace("bgp router-id {$bgpRouterId}\n", "\n")    

if network_address:    
    nixos_config = nixos_config.replace("{$networkAddress}", "\n".join(network_address))
else:
    nixos_config = nixos_config.replace("network {$networkAddress}\n", "\n")
    

if neighbor_configurations:
    nixos_config = nixos_config.replace("{$neighborConfigurations}", "\n".join(neighbor_configurations))
else:
    nixos_config = nixos_config.replace("network {$networkAddress}\n", "\n")    

# Ausgabe der NixOS-Konfiguration
print(nixos_config)
