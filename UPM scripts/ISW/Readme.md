# Purpose
we manage an EXOS switch having all ports configured for netlogin. 
We would like to:
- dinamicaly disable netlogin when an ISW switch is connected and identified behind a port
- dinamicaly enable netlogin when the port go down


## Problem 1 - ISW up:
ISW switches doesn't sent LLDP MED manufacturer information so, the EVENT.DEVICE_MANUFACTURER_NAME variable cannot be used to identify this kind of devices.
We can identify ISW switches using their MAC OUI.
Once ISW switch is identified, we'll disable netlogin on that port and set a display string on the same port.

 

## Problem 2 - ISW down:
disabling netlogin, the device-undetected trigger will not be rised up.
We can only trigger the port down event via syslog.





