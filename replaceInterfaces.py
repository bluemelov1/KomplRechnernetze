#Examples
nixos_config = '''
 interfaces.eth1 = {
      useDHCP = false;
    };
    interfaces.eth0 = {
      useDHCP = false;
      ipv4.addresses = [{
        address = "192.168.100.4";
        prefixLength = 24;
      }];
    };
    interfaces.eth2 = {
      useDHCP = false;
    };
'''

interface_mapping = {
    "eth0": "enp0s3",
    "eth1": "enp0s8",
    "eth2": "enp0s9"
}



def replace_interface_names(nixos_config, interface_mapping):
    # Replace interface names in NixOS configuration
    for vyos_interface, nixos_interface in interface_mapping.items():
        nixos_config = nixos_config.replace(vyos_interface, nixos_interface)

    return nixos_config

updated_nixos_config = replace_interface_names(nixos_config,interface_mapping)

print(updated_nixos_config)

