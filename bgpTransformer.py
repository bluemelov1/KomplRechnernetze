import json

# VyOS-Konfigurationspfad
vyos_config_path = "szenario3/vyos/bgp_router_0/config.json"

# NixOS-Template-Pfad
nixos_template_path = "bgpTemplates/bgptemplate.txt"

# Lesen der VyOS-Konfiguration aus der Datei
with open(vyos_config_path) as file:
    vyos_config = json.load(file)

# BGP-Parameter aus der VyOS-Konfiguration extrahieren
bgp_as_number = vyos_config.get("protocols", {}).get("bgp", {}).get("system-as", "")
bgp_router_id = vyos_config.get("protocols", {}).get("bgp", {}).get("parameters", {}).get("router-id", "")
network_address = vyos_config.get("protocols", {}).get("bgp", {}).get("address-family", {}).get("ipv4-unicast", {}).get("network", {}).keys()
neighbor_ip = list(vyos_config.get("protocols", {}).get("bgp", {}).get("neighbor", {}).keys())[0]
neighbor_as_number = vyos_config.get("protocols", {}).get("bgp", {}).get("neighbor", {}).get(neighbor_ip, {}).get("remote-as", "")


# Lesen des NixOS-Templates aus der Datei
with open(nixos_template_path) as file:
    nixos_template = file.read()

# Platzhalter in NixOS-Vorlage ersetzen
nixos_config = nixos_template.replace("{$bgpAsNumber}", bgp_as_number)
nixos_config = nixos_config.replace("{$bgpRouterId}", bgp_router_id)
nixos_config = nixos_config.replace("{$networkAddress}", "\n".join(network_address))
nixos_config = nixos_config.replace("{$neighborIp}", neighbor_ip)
nixos_config = nixos_config.replace("{$neighborAsNumber}", neighbor_as_number)

# Ausgabe der NixOS-Konfiguration
print(nixos_config)
