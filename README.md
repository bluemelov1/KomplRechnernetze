# Complex internship: computer networks
## Motivation 
This internship aims to investigate the potential benefits for replacing VyOS, an open-source network operating system, with a NixOS configuration. Background for this is that building VyOS is like fighting an uphill battle. The requirered packages and dependencies to build VyOS are endless and need a specialist to solve. 
NixOS on the other side has it advantages in its reproducibility of packages, which means that packages are isolated from another and have no dependencies on each other.
The question to ask now is: can we use the advantages of NixOS and reproduce the functionality of VyOS with it? 

To resolve this we are going to analyse the networking functionality of VyOS. Then we derive 3 real world szenarios which include sub-functions of VyOS. These szenarios will then be build by using NixOS. To complete our proof-of-concept we will write a translator which converts a VyOS configuration, with the functinoality of the 3 szenarios, to the nixos configuration, so that afterwards both systems have the same scope of functions.

## Requirement analysis 
This secction is going to analyse the use cases and functionality of VyOS. 

VyOS, a versatile network operating system and offers a wide range of use cases we will discuss some of them here. 

- VyOS supports various routing protocols such as OSPF, BGP, RIP, and static routing, allowing for efficient network connectivity and routing decisions
- It supports VPN technologies including IPsec, OpenVPN, L2TP, and PPTP, enabling secure remote access and site-to-site connectivity.
- VyOS offers firewall functionality with stateful packet inspection, allowing administrators to control traffic flow and enforce security policies.
- Quality of Service (QoS) features in VyOS enable traffic prioritization and bandwidth management, ensuring optimal network performance.
- It supports Network Address Translation (NAT) capabilities for IP address translation between private and public networks, enabling Internet connectivity for internal devices.
- VyOS can function as a DHCP server, providing automatic IP address assignment and configuration to client devices on the network.
- The system supports Virtual LAN (VLAN) functionality, enabling network segmentation and isolation for better security and performance.
- VyOS offers Dynamic DNS (DDNS) support, allowing devices with dynamic IP addresses to be easily accessible via domain names.
- It supports policy-based routing, enabling the routing of traffic based on specific criteria such as source IP address, protocol, or application.
- VyOS has extensive IPv6 support, allowing for seamless integration and transition to the newer IP protocol.
- The operating system offers high availability features such as VRRP (Virtual Router Redundancy Protocol) and clustering, ensuring network resilience and redundancy.
- VyOS can be deployed on various hardware platforms, including physical servers, virtual machines, and cloud environments, providing flexibility and scalability.
- It supports Multi-WAN load balancing and failover, distributing network traffic across multiple Internet connections for improved performance and reliability.
- VyOS offers a command-line interface (CLI) and a web-based management interface, providing multiple options for configuration and administration.

These use cases demonstrate the versatility and extensive capabilities of VyOS in addressing various network infrastructure requirements, from VPN deployments and cloud connectivity to enterprise edge routing and broadband access management.



The full list of configuration options for VyOS can be found in the documentation:
[https://docs.vyos.io/en/latest/configuration/index.html#configuration-guide](https://docs.vyos.io/en/latest/configuration/index.html#configuration-guide)

## Use cases 

-> divided into 3 szenarios
1. one 
2. two
3. three

-> further information in the according folders in this repository

## Approach 

-> nixos install beschreiben 


## Challenges 

-> problem only usable with internet

## Summary -> Sinnvoll? 

- for small infrastucture suitable bc more easy in the configuration but range of functions is smaller 
- give links to lookup different settings and further reading 
