# Complex internship: computer networks
## Motivation 
This internship aims to investigate the potential benefits for replacing VyOS, an open-source network operating system, with a NixOS configuration. Background for this is that building VyOS is like fighting an uphill battle. The requirered packages and dependencies to build VyOS are endless and need a specialist to solve. 
NixOS on the other side has it advantages in its reproducibility of packages, which means that packages are isolated from another and have no dependencies on each other.
The question to ask now is: can we use the advantages of NixOS and reproduce the functionality of VyOS with it? 

To resolve this we are going to analyse the networking functionality of VyOS. Then we derive 3 real world scenarios which include sub-functions of VyOS. These scenarios will then be build by using NixOS. To complete our proof-of-concept we will write a translator which converts a VyOS configuration, with the functinoality of the 3 scenarios, to the nixos configuration, so that afterwards both systems have the same scope of functions.

## Background 
### VyOS

VyOS, a versatile network operating system and offers a wide range of use cases we will list some of them here. 

- VyOS supports various routing protocols such as OSPF, BGP, RIP, and static routing
- It supports VPN technologies including IPsec, OpenVPN, L2TP, and PPTP, enabling secure remote access and site-to-site connectivity
- VyOS offers firewall functionality, allowing administrators to control traffic flow and enforce security policies
- It supports Network Address Translation (NAT)
- VyOS can function as a DHCP server, providing automatic IP addresses to client devices on the network.
- The system supports Virtual LAN (VLAN) functionality, enabling network segmentation
- VyOS supports IPv6.
- The operating system offers high availability features such as VRRP (Virtual Router Redundancy Protocol), ensuring network resilience and redundancy.
- VyOS can be deployed on various hardware platforms, including physical servers, virtual machines, and cloud environments, providing flexibility and scalability.
- It supports Multi-WAN load balancing and failover, distributing network traffic across multiple Internet connections for improved performance and reliability.
- VyOS offers a command-line interface (CLI) and a web-based management interface, providing multiple options for configuration and administration.

The full list of configuration options for VyOS can be found in the documentation:
[https://docs.vyos.io/en/latest/configuration/index.html#configuration-guide](https://docs.vyos.io/en/latest/configuration/index.html#configuration-guide)

While VyOS offers several advantages, it comes at a price that goes beyond monetary considerations. Although it is an open-source solution, utilizing VyOS effectively can be quite expensive in terms of knowledge and expertise. Building VyOS from source code is a cumbersome process due to its reliance on various packages, not to mention the complexities involved in customizing the system to suit specific needs. This requires a significant investment of time and effort to gain a comprehensive understanding of VyOS.

### NixOS

NixOS is a Linux distribution known for its unique package management and system configuration approach. 
It is based on the Nix package manager, offering a declarative way to manage software and system settings. 
One of its key advantages is the ability to manage packages independently, meaning each package and its dependencies are isolated and self-contained. 
This approach avoids conflicts and ensures that upgrading or removing a package does not impact other parts of the system. 
Upgrades in NixOS are designed to be performed as a whole, ensuring the entire upgrade process is reliable and can be easily reversed if needed.
With NixOS, the entire operating system is defined by a single configuration file, allowing for reproducible setups. 
To conclude NixOS is famous due to its reproducibility, reliability, flexibility, and the independent nature of its packages.


## Task
To demonstrate the advantages of NixOS and show its ability to provide similar functionality as VyOS, we will replicate three specific [use cases](#use-cases) in both VyOS and NixOS configurations. Additionally, we will develop a generic transformer that takes a VyOS configuration as input and generates a corresponding NixOS configuration.

The transformer will automate the process of migrating from VyOS to NixOS for the specified use cases, ensuring a smooth transition and replication of functionality.

While the initial transformer implementation will focus on the specified use cases, it can be extended by mapping additional files and configurations to cover more scenarios. 
This flexibility allows for customization and adaptation of the transformer to suit specific needs beyond the initial use cases.
For further information see [Transformer](#vyos-to-nixos-transformer).

By successfully replicating the use cases and providing a tool to transform VyOS configurations into NixOS configurations, we aim to highlight NixOS's ability to offer comparable functionality to VyOS while using its unique features such as package isolation, reproducibility, reliability.


## Requirement analysis 

This section lists all requirements to complete this internship.

- R1: Analyse the functionality of VyOS and NixOS
- R2: Derive three use cases of VyOS and build the scenarios using NixOS 
- R3: Develop a transformer to convert VyOS configurations to NixOS configurations
- R4: Assess the advantages and disadvantages of replacing VyOS with NixOS 


## Use cases 
For our proof of concept we choose some realistic use cases, where we provide the VyOS functionality by NixOS. While defining our goal we divided our use cases by komplexity. 

The first one rebuilds a DHCP server with three clients that automatically receive an ip-addresses. Additionally to the DHCP we configured a bonding interface between two NixOS systems. 

In the second scenario we configure a wireguard VPN which simulates a remote worker to be connected to an onsite network.

The third scenario addresses the routing functionality of a VyOS device. Therefore we configure three routers automatically exchanging network topology information as autonomous systems. 

Further description and explanation about the scenarios can be found in the according folders in this repository. 

## Approach 

### NixOS installation
To set up the scenarios, we choose VirtualBox as our virtualization tool. VirtualBox is a free and open-source software that enables the creation and operation of multiple virtual machines on a single physical computer. This choice helps minimize research costs since no specialized equipment is required.

To begin, we downloaded the minimal ISO of NixOS from the official website: 
[https://nixos.org/download.html#nixos-iso](https://nixos.org/download.html#nixos-iso)

We selected the minimal ISO because it offers lighter system requirements, which is beneficial when running four virtual machines simultaneously. There is also no the need for graphical software in our scenarios. Because of that, the command-line interface suits our purposes.

Next, we installed the ISO onto a newly created virtual machine, following the instructions provided on the NixOS website: https://nixos.org/manual/nixos/stable/index.html#sec-installation-manual-partitioning.

Once the virtual machine was operational, we proceeded to create virtual duplicates of it. These duplicates served as the starting point for our scenarios.


### VyOS to NixOS transformer

#### What it does?

To complete our proof of concept we designed a translator which takes a VyOS configruation as an input and gives you a NixOS configuration as an output. This is possible for our four use cases: 
1. DHCP server
2. Bonding
3. Wireguard configuration
4. BGP router 

#### How to use it? 

1. To obtain the VyOS ocnfiguration of a running system you can utilize one of the following commands: 
```
show configuration > config.json
show configuration json pretty >config.json # only from version 1.3 available
```
(Before proceeding, ensure that Python 3 is installed on your NixOS system. )

2. Next, transfer the 'config.json' file along with the '/transformer/*' directory from this repository to your active NixOS system. Ensure that the 'config.json' file is located next to the 'transformer.py' file. 

3. Proceed by running the 'transformer.py' script. After completion, it will generate a 'configuration.nix' file. 

4. Copy the 'confiuration.nix' file to '/etc/nixos/configuration.nix' and apply it to the system by executing: 
```
nixos-rebuild switch
```


#### How does it work? 
The algorithm converts a VyOS configuration files in JSON format to Nix configuration files in Nix format. 
It accomplishes this by taking into account the VyOS configuration and mappings, which are created for each transformation scenario.
The VyOS configuration is extracted from an active system, allowing the algorithm to work directly with real-world data. On the other hand, the mappings are manually designed and stored in the "/transformer/mappings/" directory. These mappings follow a specific syntax, explained in the [section](#internal-mapping-syntax).
The mapping files can be expanded to cover additional services or functionalities, providing flexibility for future extensions.

The transformer itself is divided into three parts. 

The preprocessor, which is responsible for collecting the data and processing the representation. Notably, it analyses the network interfaces of the NixOS system to ensure that they are configured with the appropriate name in the nix configuration. 

The mainprocessor is responsible for applying the specified rules of the mapping files to the extracted information from vyos and translate it to nixos config. 
This involves an iterative algorithm that scans for matches from the mapping file within the VyOS data.
The algorithm supports two types of placeholders. The first type, $X (where X is any positive integer starting from 0), stores the value of the VyOS configuration at that place in a list indexed correspondingly, which can later supplement the Nix path. The second type involves the use of regular expressions. Here, the algorithm compares the value from the VyOS configuration at that place with the regex. If a match is found, the algorithm continues comparing the paths from VyOS with the mapping path until it verifies a full match. The use of regular expressions also allows for group matches with round brackets. These groups are added separately to the list of stored values and can be utilized within the NixOS configuration path of the mapping. For each match, the configuration is immediately translated and stored in the NixOS configuration.

The postprocessor, is designed to handle special configuration files for service use cases such as DHCP and BGP. These configurations, while included in the configuration.nix file, follow a different syntax and require special considerations during creation. For instance, unlike pure Nix config syntax, DHCP and BGP syntax can contain repeated sections requiring unique mapping treatment. You can find a more detailed comparison in the [Challenges](#challenges) section.

After all the processing stages, the main file combines all the configurations into a single string and exports it to the 'configuration.nix'.


#### Transformer concept
- The program takes a VyOS configuration file in JSON format as input.
- It defines several helper functions to process and manipulate the configuration data.
- The function generate_entry_strings generates a list of entry strings from the VyOS configuration data. Each entry string represents a key-value pair in the configuration.
- The check function recursively checks the VyOS configuration keywords against a mapping dictionary. It uses depth-first search to match the keywords with the mapping entries. If a match is found, it stores the corresponding arguments in a dictionary.
- The vyos_path_to_nixos_path function translates a NixOS configuration path by replacing argument placeholders with their corresponding values from the args dictionary.
- The parseToNixConfig function processes the checking result data, groups it based on the mapping, and translates it into NixOS configuration format.
- The program demonstrates the usage of these functions by reading the VyOS configuration file, performing checks, and generating NixOS configuration statements based on the mapping.

#### Internal Mapping syntax
--> Describe in JSON format
interfaces#wireguard#$0#peer#client#address=$1;nterfaces#wireguard#$2#port=$3@networking.wireguard.interfaces.$0.peers.endpoint=$1:$3;
Let's break down how this mapping works:

The mapping applies to VyOS configuration lines related to WireGuard interfaces.

#$0# represents a placeholder that captures the first element from the VyOS configuration line. The value captured by this placeholder will be used later in the Nix configuration line.

The mapping specifies the property address=$1 for a WireGuard peer with the tag client. It captures the value of $1 from the VyOS configuration line, which represents the peer's address.

#$2# represents another placeholder that captures the third element from the VyOS configuration line. The value captured by this placeholder will be used later in the Nix configuration line.

port=$3 specifies the port property for the WireGuard peer. It captures the value of $3 from the VyOS configuration line, which represents the port number.

@networking.wireguard.interfaces.$0.peers.endpoint=$1:$3 represents the Nix configuration line that will be generated based on the VyOS configuration line.

In the Nix configuration line, $0 is replaced with the value captured by the #$0# placeholder from the VyOS configuration line.

$1 is replaced with the captured peer address, and $3 is replaced with the captured port number.

The resulting Nix configuration line sets the endpoint property for the WireGuard interface's peer, combining the captured peer address and port number.

In summary, this mapping translates a VyOS configuration line related to a WireGuard interface's peer address and port into a Nix configuration line that sets the corresponding endpoint property for the peer in the Nix configuration. It captures the necessary values from the VyOS configuration line using placeholders and inserts them into the appropriate positions in the Nix configuration line.


system#host-name=$0@networking.hostName="$0";
Here's a brief explanation of how it works:

The mapping applies to the VyOS system configuration line that sets the host name.

The placeholder =$0 captures the value of the first element from the VyOS configuration line, representing the desired host name.

In the Nix configuration line, networking.hostName="$0" assigns the captured host name value to the hostName property in the networking section.

The placeholder $0 is replaced with the captured host name value from the VyOS configuration line.

In summary, this mapping translates a VyOS system configuration line that sets the host name into a Nix configuration line that assigns the same host name to the networking.hostName property. It captures the desired host name value using the placeholder $0 and inserts it into the Nix configuration line.


```
vyos_config_path_1:nixos_config_path_1
vyos_config_path_2:nixos_config_path_2

```

once you have the configuration of vyos you can go on. Next you need to have a running NixOS instance with python installed. then you copy the vyos config togeather with the transformer.py script in this repository to the NixOS maschiene

- vyos_config_path: This is the path to a specific configuration key in the VyOS configuration. It follows the format of nested keys separated by # (e.g., 'interfaces#bonding#$0#hash-policy').
  - If a key contains an argument placeholder, it should be denoted by starting with $ followed by the index of the argument (e.g., 'interfaces#bonding#$0#address').
  - If a vyos config value should be tranformed into a other representation on the nixos side you can use a regular expression match, it can be specified by appending ~ followed by the regular expression pattern (e.g., 'interfaces#bonding#$0#address~^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/(\d{1,2})$') at the end of the vyos_config_path side.
    - every group in the regex need a corresponding nixos keyword 
    - the corresponding nixos keywords can be specified by appending ~ followed by the keywords (sparated with ";") (e.g., networking#$0#address~adress;prefixLength') on the nixos_config_path side
- nixos_config_path: This is the corresponding path to the desired location in the NixOS configuration where the VyOS configuration key should be translated. It uses the same nested key format as in VyOS (e.g., 'networking#hostName').


## Challenges 

-> problem only usable with internet (more of a secutiry gap that a real switch?)

-> VyOS and NixOS deamons for DHCP using different approach for selecting the network in which they route: VyOS uses subnet and NixOS uses interfaces 
    additionally nixos requires more specific configrutation and vyos is more user friendly


## Summary -> Sinnvoll? 
With our three scenarios we covered the widest area of functions in our short time. Because NixOS and VyOS are both using the linux kernel they will likely run on the same maschines and can run similar drivers. Therefore the advantage of VyOS that it can be deployed on various hardware plattforms is removed. Furthermore VyOS benefits from an CLI and an web-based management. NixOS on the other side is accessed by a linux CLI for local configuration. Remote access is also possible by ssh which is not as convinient as a GUI on a website but has exactly the same possibilities.


- for small infrastucture suitable bc more easy in the configuration but range of functions is smaller 
- give links to lookup different settings and further reading 

- bigger security issues for nixos
- not so specialized, so in specific configuration may be more cumbersome to configure than vyos once youre familliar with both languages








# Not required anymore:

#### Transformer usage guide
1. In Vyos: write vyos json representation into config.json file
```
show configuration json pretty > config.json
```
2. In Nixos: add generated config.json to directory of transformer.py
3. add mapping files to mappings directory
4. run transformer.py
5. newly generated configuration.nix now available in same directory


