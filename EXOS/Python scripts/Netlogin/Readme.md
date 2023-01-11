## Purpose
I have created the scripts in the current directory to help in the deployment and management of a Extreme Networks NAC system.

## Enable_netlogin_global.py
This script shall be run from XIQ-SE (or XMC) to configure and enable the netlogin at the switch level: Radius servers, authentication VLAN, ...
It works on Extremeware and EXOS switches running at least a 15.0 firmware.

## Enable_netlogin_onPorts.py
This script shall be run from XIQ-SE (or XMC) to enable the netlogin on selected switch ports. It delete the current VLANs and activate netlogin (dot1x and mac) in mac-based-vlans mode.
It works on Extremeware and EXOS switches running at least a 15.0 firmware.

## Create_netlogin_localdb.py
This Python script create the netlogin local database that can be used if both the NAC servers are unreachable.
It can be saved on the switch flash and executed periodically or it can be executed via a workflow on XIQ-SE (or XMC).
