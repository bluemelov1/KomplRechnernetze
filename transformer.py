import copy

import preprocessor
import mainprocessor
import postprocessor

#VyOS_path = "szenario1/vyos/bonding/config.json"
VyOS_path = "szenario1/vyos/dhcp/dhcp-server.json"

vyos_config = preprocessor.get_vyos_config(VyOS_path)

mappings = preprocessor.get_mapping_as_dict('mappings')

preprocessor.print_mapping(mappings)

checking_result_data = []

for vyos_config_path in vyos_config:
    vyos_config_sep = vyos_config_path.split("=")
    vyos_config_keywords = vyos_config_sep[0].split("#")

    mapping_hit = copy.deepcopy(mappings)
    args = {}

    checking_hit = mainprocessor.check(vyos_config_keywords, mapping_hit, args, 0)

    if checking_hit:
        checking_result_data.append({
            "mapping" : mapping_hit,
            "args" : args,
            "vyos_config_value" : vyos_config_sep[1]
        })
        print(f"\nVyos Config Path: " + vyos_config_path)
        print("Config Value: ", vyos_config_sep[1])
        print("Mapping Hit: ", checking_hit)
        print("Mapping entry: ", mapping_hit)
        print("Extracted Args: ", args)
    
print(mainprocessor.parseToNixConfig(checking_result_data))


### if dhcp server do postprocessor dhcp server ... 
print(postprocessor.get_dhcp_configuration(vyos_config))
### an richtige stelle in nixConfig einfügen !!!

