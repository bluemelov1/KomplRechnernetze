# Complex internship: computer networks
## Motivation 
This internship aims to investigate the potential benefits for replacing VyOS, an open-source network operating system, with a NixOS configuration. Background for this is that building VyOS is like fighting an uphill battle. The requirered packages and dependencies to build VyOS are endless and need a specialist to solve. 
NixOS on the other side has it advantages in its reproducibility of packages, which means that packages are isolated from another and have no dependencies on each other.
The question to ask now is: can we use the advantages of NixOS and reproduce the functionality of VyOS with it? 

To resolve this we are going to analyse the networking functionality of VyOS. Then we derive 3 real world scenarios which include sub-functions of VyOS. These scenarios will then be build by using NixOS. To complete our proof-of-concept we will write a translator which converts a VyOS configuration, with the functinoality of the 3 scenarios, to the nixos configuration, so that afterwards both systems have the same scope of functions.

## Requirement analysis 
This secction is going to analyse the use cases and functionality of VyOS. 

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


-> go more into nixos advantages and why we use it, explain what we expect out of it and the function of the translator

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


### VyOS to NixOS translator
To complete our proof of concept we designed a translator which takes a VyOS configruation as an input and gives you a NixOS configuration as an output. This is possible for our four use cases: 
1. DHCP server
2. Bonding
3. Wireguard configuration
4. BGP router 

To obtain the VyOS ocnfiguration of a running system you can use the following command: 
```
show configuration 
show configuration json pretty  # only from version 1.3 available
```


-> translator von VyOS config zu NixOS config beschreiben und erklären 


## Challenges 

-> problem only usable with internet (more of a secutiry gap that a real switch?)

## Summary -> Sinnvoll? 
With our three scenarios we covered the widest area of functions in our short time. Because NixOS and VyOS are both using the linux kernel they will likely run on the same maschines and can run similar drivers. Therefore the advantage of VyOS that it can be deployed on various hardware plattforms is removed. Furthermore VyOS benefits from an CLI and an web-based management. NixOS on the other side is accessed by a linux CLI for local configuration. Remote access is also possible by ssh which is not as convinient as a GUI on a website but has exactly the same possibilities.


- for small infrastucture suitable bc more easy in the configuration but range of functions is smaller 
- give links to lookup different settings and further reading 
