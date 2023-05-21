# DHCP setup

## Usecase
- receive a network configuration via DHCP server in the local network
- 3 actors: two clients and one DHCP Server
- each actor is based on NixOS
- client and actor differ in their configuration file (more details below)

## Implementation

## DHCP Server configuration
### Interface configuration
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

### DHCP server configuration
- enable DHCPv4 Server
```
enable = true;
```
- configure that DHCP server should listen on new created interface
```
interface = ["enp0s8"];
```
- configure subnet, subnet-mask, broadcast-address, interface (must be selected because their could be other interface which also use DHCP and serve other subnetworks
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

### Complete configuration snippet
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

## Client configuration
### Interface configuration
- add interface / adapter to internal network
- enable that interface obtain network configuration via DHCP
``` 
useDHCP = true;
```
### Complete configuration snippet
```
networking = {
  hostName = "nixos-client-0"; # Define your hostname.
  defaultGateway = "";
  interfaces.enp0s8 = {
    useDHCP = true;
  };
}; 
```

## Problems
At the beginning it was a bit confusing, because all virual machines with were connected to the internal network already got a functional IP address to communicate in the internal network.
This was caused by the fact that Virtualbox already got a DHCP server running which gave our machines a basic network configuration for the internal network.
An other problem was that we were not shure about how we should edit the configuration file on the respective maschines without being forced to do it manuelly on every maschine. And connected to this problem, we were searching for a solution to manage our configuration file via GitHub without being forced to use git on the maschines them self. Our solution to these problemes was a feature from Virtualbox which is called "shared folder". This feature allowed us to share a fold from the filesystem of our host operating system, with a fold from the filesystem of our virtual maschine. At the end we shared the folder which represented our Git-repository with the virtual maschine, which allowed use to edit, versionize and deploy our changes more efficient.
- 
