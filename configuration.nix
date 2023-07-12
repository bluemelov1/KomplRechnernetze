{ config, pkgs, ...}:
{
  imports =
    [
      ./hardware-configuration.nix
    ];
  boot.loader.grub.enable = true;
  boot.loader.grub.version = 2;
  boot.loader.grub.device = "/dev/sda";

networking.interfaces.eth2.ipv4.addresses=[{address="192.168.111.1";prefixLength=$2;}];
networking.interfaces.br-44ea4feaa2e8.ipv4.addresses=[{address="10.0.0.1";prefixLength=$2;}];
services.dhcpd4.enable = true;
services.dhcpd4.interfaces = "eth2" ;
services.dhcpd4.extraConfig = ''
  option subnet-mask 255.255.255.0;
  subnet 192.168.111.0/24 netmask 255.255.255.0 {
      option broadcast-address 192.168.111.255;
      option routers 192.168.111.1;
      interface eth2;
      range 192.168.111.2 192.168.111.10;
  }
'';

services.frr.bgp = {
  enable = true;
  config = ''
    router bgp 65000
      bgp router-id 10.0.0.1
      no bgp ebgp-requires-policy
    network 192.168.111.0/24
    neighbor 10.0.0.2 remote-as 65001
    redistribute connected;
  '';
};
  environment.systemPackages = with pkgs; [
    vim
    frr
  ];
  system.stateVersion = "22.11";
}
