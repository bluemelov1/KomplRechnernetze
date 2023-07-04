# Bonding setup

## Usecase
This example aims at rebuilding the bonding/link aggregation functionality of VyOS. Bonding is a technology used to increase fault tolerance and load balancing by conbining multiple network interface cards (nics) into one logical. 

The setup is build by two virtual maschines using VirtualBox, which are directly connected to two interfaces of your host system. To prove the increased avaiability of this setup we deactivate one link and still keep the connection to the other OS alive. 

## Configuration

### Adding virtual interfaces 

To create interfaces on the host maschine over which the virtual maschines (VMs) can connect to each other you need to execute the following:
```
ip tuntap add p1 mode tap
ip tuntap add p2 mode tap
```
This adds virtual interfaces to your host which operate at layer 2 and can be used to bridge network traffic.


After you initialized the interfaces you need to activate them.
```
ip link set dev p1 up
ip link set dev p2 up
```

### Settings in VirtualBox

Connecting the VMs to each other you have to add two additional nics to each VM and configure them as shown in the picture. 

The first nic is used for internet connection and the 2nd and 3rd will be used for the bonding.

![Network configuration of the VMs in VirtualBox](img/networkConfigVB.png)


### Configuration of NixOS

Configuring bonding with the NixOS configuration file can be accomplished in three different ways:
* using systemd.network
* install netplan and configure .yaml
* use NixOS internal networking setction

We chose the third option because it's the simplest and most straightforward approach.

The following network configuration configures the bond interface. First you have to set a hostname and disable the DHCP client for the two interfaces (in this case 'enp0s8' and 'enp0s9'). The third interfaces section configures the 'bond0' interface by setting the IP-address and the subnet and deactivating the DHCP client aswell. The bonds section creates actual bonds with their specific settings. The interfaces option allows you to choose the interfaces that schould be used as slaves by the bond. Within the driverOptions you can configure all the attributes explained in the following manpage. 
[https://www.kernel.org/doc/Documentation/networking/bonding.txt](https://www.kernel.org/doc/Documentation/networking/bonding.txt)

To get everything up and running you need to add this lines to the file at "/etc/nixos/configuration.nix". For the second VM you need to change the hostName and the IP-address of the bond interface (e.g. "192.169.100.3").


```
  networking = {
    hostName = "host-1";
    defaultGateway = "";
    interfaces.enp0s8 = {
      useDHCP = false;
    };
    interfaces.enp0s9 = {
      useDHCP = false;
    };
    interfaces.bond0 = {
      useDHCP = false;
      ipv4.addresses = [{
        address = "192.168.100.2";
        prefixLength = 24;
      }];
    };
    bonds = {
      bond0 = {
        interfaces = [ "enp0s8" "enp0s9" ];
        driverOptions = {
          miimon = "100";
          mode = "active-backup";
          primary = "enp0s8";
          fail_over_mac = "active";
        };
      };
    };
  };
```

After you added this to your configuration.nix file you can run the command to rebuild the system and apply all changes. 

```
sudo nixos-rebuild switch
```

# Testing 
To be sure that the bond interfaces are workung correctly we can look up the current state of the nics with the command:
```
ip a
```
![Configuration of all network interfaces](img/ipA.png)

If we want to get a more concrete setting of the bond interface we can read the following file by:

```
cat /proc/net/bonding/bond0
```
![Configuration of a bond interface](img/bondConfig.png)

The fault-tolerance improvement can be tested and simulated by deactivating the active slave interface while pinging the other VM and see that there is no disturbance. So we start by pinging the VM. Then we use the following command to deactivate the interface on the other VM which was set as 'Currently Active Slave' in the bond configuration. 

```
ip link set dev enp0s8 down
```

If we then look at the bond interface configuration we see that the 'Currently Active Slave' has changed but the connection is still active.

## Problems
In the process of building this setup there where mainly two obsacles. The first was about NixOS which did not apply the configuration changes after using 'nixos-rebuild switch' therefore I used a new clone from my initial instance.

The other obstacle is to read the manual of the bonding configuration carefully to be sure that your config is valid. You find that at: 
[https://www.kernel.org/doc/Documentation/networking/bonding.txt](https://www.kernel.org/doc/Documentation/networking/bonding.txt)


## VyOS configuration of bonding

*Create bond ad set mode*
```
set interfaces bonding bond0 mode 802.3ad
```

*Give address to bond*
```
set interfaces bonding bond0 address 10.1.1.1/24
```

*add interface to the bond-group (vyos 1.3)*
```
set interfaces bonding bond0 member interface eth0
set interfaces bonding bond0 member interface eth1
```

*set primary bond interface*
```
set interfaces bonding bond0 primary eth0
```

See further commands [here](https://docs.vyos.io/en/latest/configuration/interfaces/bonding.html)