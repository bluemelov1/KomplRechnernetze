import copy
import re 

import preprocessor
import mainprocessor
import postprocessor

#VyOS_path = "szenario1/vyos/bonding/config.json"
VyOS_path = "szenario1/vyos/dhcp/dhcp-server.json"
#VyOS_path = "szenario1/vyos/dhcp/dhcp-client.json"
#VyOS_path = "szenario2/vyos/config-server.json"
#VyOS_path = "szenario3/vyos/client_0/config.json"
#VyOS_path = "szenario3/vyos/bgp_router_0/config.json"

mapping_path = "mappingsJSON/mappings.json"

vyos_config = preprocessor.get_vyos_config(VyOS_path)

#mappings = preprocessor.get_mapping_as_dict('mappings')

#preprocessor.print_mapping(mappings)

mappings = preprocessor.get_internal_mapping_syntax(mapping_path)
preprocessor.print_mapping(mappings)

'''
Theorie:

- Einlesen des mappings
- aufteilen eingabe ausgabe
- aufteilen eingabe falls nötig
- (aufteilen ausgabe falls nötig)

    - suche von match für alle eingaben, speichern der $x und überprüfen der Regeln
'''
nix_config_str = ""
nix_main = mainprocessor.extract_dollars(vyos_config, mappings, VyOS_path)
for line in nix_main:
    nix_config_str += line + "\n"  

interface_mapping = postprocessor.create_interface_mapping("szenario3/vyos/bgp_router_0/config.json")
nix_updated = postprocessor.replace_interface_names(nix_config_str, interface_mapping)
print(nix_updated)
#for line in nix_updated:
#    print(line)





