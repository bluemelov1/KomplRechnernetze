import os
import json
import subprocess

vyos_config_file = "config-server.json"

# JSON-Datei einlesen
with open(vyos_config_file, "r") as f:
    vyos_config = json.load(f)

vyos_network_config = vyos_config.get("interfaces", {})

interfaces_vyos = []

# Ethernet-Interfaces sammeln
if "ethernet" in vyos_network_config:
    ethernet_interfaces = vyos_network_config["ethernet"]
    interfaces_vyos.extend(list(ethernet_interfaces.keys()))

# # Loopback-Interfaces sammeln
# if "loopback" in vyos_network_config:
#     loopback_interfaces = vyos_network_config["loopback"]
#     interfaces_vyos.extend(list(loopback_interfaces.keys()))

# WireGuard-Interfaces sammeln
if "wireguard" in vyos_network_config:
    wireguard_interfaces = vyos_network_config["wireguard"]
    interfaces_vyos.extend(list(wireguard_interfaces.keys()))

# Ausführung des Befehls "ip a" und Erfassung der ausgegebenen Interfaces
command = "ip a"
output = subprocess.check_output(command, shell=True).decode("utf-8")

interfaces_nixos = []

# Verarbeiten der Ausgabe von "ip a" und Erfassen der Interfaces
lines = output.splitlines()
for line in lines:
    if line[0].isdigit():
        # Zeile enthält ein Interface
        parts = line.split(":")
        interface = parts[1].strip()
        if not interface.startswith("lo"):  # Loopback interface skippen
            interfaces_nixos.append(interface)
# Mapping-Dictionary erstellen
interface_mapping = {}

# Interfaces abbilden
for vyos_interface in interfaces_vyos:
    if interfaces_nixos:
        # NixOS-Interface für VyOS-Interface finden und zuordnen
        nixos_interface = interfaces_nixos.pop(0)
        interface_mapping[vyos_interface] = nixos_interface
    else:
        # Keine weiteren NixOS-Interfaces vorhanden, Mapping abbrechen
        break

# Beispiel: Ausgabe des Interface-Mappings
for vyos_interface, nixos_interface in interface_mapping.items():
    print(f"VyOS Interface: {vyos_interface} --> NixOS Interface: {nixos_interface}")



# wireguard cmd Befehle
# import subprocess

# # Befehle ausführen
# commands = [
#     "nix-env -iA nixos.wireguard-tools",
#     "umask 077",
#     "mkdir ~/wireguard-keys",
#     "wg genkey > ~/wireguard-keys/private",
#     "wg pubkey < ~/wireguard-keys/private > ~/wireguard-keys/public"
# ]

# for command in commands:
#     subprocess.run(command, shell=True, check=True)