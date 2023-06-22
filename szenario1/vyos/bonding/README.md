# Copy files from VM to host machine 
## create an interface for exchanging files

on host 
```
sudo ip tuntap add dev p3 mode tap
sudo ip addr add dev p3 10.10.10.1/24
sudo ip link set dev p3 up
```
add additional nic in virtualbox to the vm and connect p3
on vyos system
```
configure
set interface ethernet eth2 address 10.10.10.2/24
commit
save 
exit

python3 -m http.server
```

on host machine search in browser for "10.10.10.2:8000" and download the files




# Create bond ad set mode
set interfaces bonding bond0 mode 802.3ad
# Give address to bond
set interfaces bonding bond0 address 10.1.1.1/24

# add interface to the bond-group (vyos 1.2)
set interfaces ethernet eth0 bond-group bond0

# add interface to the bond-group (vyos 1.3)
set interfaces bonding bond0 member interface eth0
set interfaces bonding bond0 member interface eth1

# set primary bond interface 
set interfaces bonding bond0 primary eth0

