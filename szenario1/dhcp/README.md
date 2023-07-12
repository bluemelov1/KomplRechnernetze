## DHCP scenario
### Use Case
- receive a network configuration via DHCP server in the local network
- 3 actors: two clients and one DHCP Server
- each actor is based on NixOS
- client and actor differ in their configuration file (more details below)

### Implementation
#### DHCP Server configuration
##### Interface configuration
- add interface / adapter to internal network
- disable that interface obtains network configuration via DHCP:
```
useDHCP = false;
```
- assign static IP-Address to new interface
```
ipv4.addresses = [{
  address = "10.1.1.1";
  prefixLength = 24;
}];
```

#### DHCP server configuration
- enable DHCPv4 Server
```
enable = true;
```
- configure that DHCP server should listen on new created interface
```
interface = ["enp0s8"];
```
- configure subnet, subnet-mask, broadcast-address, interface (must be selected because their could be other interface which also use DHCP and serve other sub networks
```
extraConfig = ''
  option subnet-mask 255.255.255.0;
  subnet 10.1.1.0 netmask 255.255.255.0 {
    option broadcast-address 10.1.1.255;
    option routers 10.1.1.1;
    interface enp0s8;
    range 10.1.1.2 10.1.1.254;
  }
'';
```

#### Complete configuration snippet
```
networking = {
  hostName = "nixos-router"; # Define your hostname.
  defaultGateway = "";
  interfaces.enp0s8 = {
    useDHCP = false;
    ipv4.addresses = [{
      address = "10.1.1.1";
      prefixLength = 24;
    }];
  };
};
  
services.dhcpd4 = {
  enable = true;
  interfaces = ["enp0s8"];
  extraConfig = ''
    option subnet-mask 255.255.255.0;
    subnet 10.1.1.0 netmask 255.255.255.0 {
      option broadcast-address 10.1.1.255;
      option routers 10.1.1.1;
      interface enp0s8;
      range 10.1.1.2 10.1.1.254;
    }
  '';
};

```

### Client configuration
#### Interface configuration
- add interface / adapter to internal network
- enable that interface obtain network configuration via DHCP
``` 
useDHCP = true;
```
#### Complete configuration snippet
```
networking = {
  hostName = "nixos-client-0"; # Define your hostname.
  defaultGateway = "";
  interfaces.enp0s8 = {
    useDHCP = true;
  };
}; 
```

### Testing
The testing in this scenario is pretty simple. We just have to start the DHCP server and the two clients. After that we can check if the clients got a valid IP address from the DHCP server. We can do this by running the following command on the clients:
```
ip a
```

### Problems
During our research, we encountered the problem, that the clients automatically received ip-addresses in a network space we did not know. Trough further research we found out that Virtualbox already got a DHCP server running which distributed our machines a basic network configuration for the internal network. 

To speed up the process of configuring NixOS in the virtual machines and copy the configurations file to the host system, we used the shared folder functionality of Virtualbox. This allowed us to edit the configuration file on the host system and deploy the changes to the virtual machines while saving them in the git repository.