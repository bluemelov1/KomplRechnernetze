# DHCP setup

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






