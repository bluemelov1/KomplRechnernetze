#!/bin/bash

interfaces=("p0" "p1" "c0" "c1")

for interface in "${interfaces[@]}"
do
    # Erstellen der Tuntap-Schnittstelle
    ip tuntap add "$interface" mode tap

    # Aktivieren der Schnittstelle
    ip link set dev "$interface" up
done

echo "Tuntap-Schnittstellen wurden erfolgreich erstellt und aktiviert."

