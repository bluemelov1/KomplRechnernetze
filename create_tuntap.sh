#!/bin/bash

interfaces=("p1" "p2" "c0")

for interface in "${interfaces[@]}"
do
    # Erstellen der Tuntap-Schnittstelle
    ip tuntap add "$interface" mode tap

    # Aktivieren der Schnittstelle
    ip link set dev "$interface" up
done

echo "Tuntap-Schnittstellen wurden erfolgreich erstellt und aktiviert."

