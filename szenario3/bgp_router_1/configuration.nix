{ config, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  # Use the GRUB 2 boot loader.
  boot.loader.grub.enable = true;
  boot.loader.grub.version = 2;
  boot.loader.grub.device = "/dev/sda"; # or "nodev" for efi only
  boot.kernel.sysctl = {
    # if you use ipv4, this is all you need
    "net.ipv4.conf.all.forwarding" = true;

    # If you want to use it for ipv6
    "net.ipv6.conf.all.forwarding" = true;
  };

  # Set your time zone.
  time.timeZone = "Europe/Berlin";


  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";
  console = {
    font = "Lat2-Terminus16";
    keyMap = "de";
  #   useXkbConfig = true; # use xkbOptions in tty.
  };

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.philipp = {
    isNormalUser = true;
    extraGroups = [ "wheel" ]; # Enable ‘sudo’ for the user.
    initialPassword = "password";
  #   packages = with pkgs; [
  #     firefox
  #     thunderbird
  #   ];
  };
  networking = {
    hostName = "bgp-router-1";
    defaultGateway = "";
    interfaces.enp0s8 = {
      useDHCP = false;
      ipv4 = {
        addresses = [{
          address = "10.0.0.2";
          prefixLength = 24;
        }];
      };
    };
    interfaces.enp0s9 = {
      useDHCP = false;
      ipv4.addresses = [{
        address = "20.0.0.2";
        prefixLength = 24;
      }];
    };
  };

  services.frr.bgp = {
    enable = true;
    config = ''
      router bgp 65001
      bgp router-id 20.0.0.2
      address-family ipv4 unicast
        network 192.168.2.0/24
      exit-address-family
      neighbor 10.0.0.1 remote-as 65000
      neighbor 20.0.0.1 remote-as 65002
    '';
  };

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
    vim 
    wget
    frr
    nettools
    nmap
  ];

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "22.11"; # Did you read the comment?

}

