#Purpose
we manage an EXOS switch having all ports configured for netlogin. 
We would like to:
- dinamicaly disable netlogin when an ISW switch is connected and identified behind a port
- dinamicaly enable netlogin when the port go down


##Problem 1 - ISW up:
ISW switches doesn't sent LLDP MED manufacturer information so, the EVENT.DEVICE_MANUFACTURER_NAME variable cannot be used to identify this kind of devices.
We can identify ISW switches using their MAC OUI.
Once ISW switch is identified, we'll disable netlogin on that port and set a display string on the same port.
The following UPM script have to be created and associated to the UPM trigger device-detected.

create upm profile ISW-up
set var macoui "d8:84:66"
set var devicemac $EVENT.DEVICE_MAC
set var devicemacoui $TCL(string range ${devicemac} 0 7)
create log message $(devicemacoui)
\#N.B.: the match function returns 0 if matched
if (!$match($devicemacoui,$macoui)) then
create log message "EXTREME ISW switch UP"
disable netlogin ports $EVENT.USER_PORT dot1x mac
configure ports $EVENT.USER_PORT display-string Extreme_ISW
configure vlan <ISW mgmt vlan> add port $EVENT.USER_PORT <tag | untagg>
configure vlan <client vlans> add port $EVENT.USER_PORT tagg
endif
.
configure upm event device-detect profile ISW-up ports <all netlogin ports>
 

##Problem 2 - ISW down:
disabling netlogin, the device-undetected trigger will not be rised up.
We can only trigger the port down event via syslog.
The following UPM script have to be created and associated to the port down log.

create upm profile ISW-down
enable cli scripting
set var cli.out 0
set var stringISW "Extreme_ISW"
show port $EVENT.LOG_PARAM_0 no-refresh | i $EVENT.LOG_PARAM_0
set var displaystring $TCL(string range ${cli.out} 5 25)
set var displaystring $TCL(string trim ${displaystring})
\#N.B.: the match function returns 0 if matched
if (!$match($displaystring,$stringISW)) then
create log message "EXTREME ISW switch DOWN"
unconfigure port $EVENT.LOG_PARAM_0 display-string
configure vlan <ISW mgmt vlan> del port $EVENT.LOG_PARAM_0
configure vlan <client vlans> del port $EVENT.LOG_PARAM_0
enable netlogin ports $EVENT.LOG_PARAM_0 dot1x mac
configure netlogin ports $EVENT.LOG_PARAM_0 mode mac-based-vlans
configure netlogin ports $EVENT.LOG_PARAM_0 no-restart
endif
disable cli scripting
.

create log filter upmFilter
configure log filter upmFilter add events vlan.msgs.portLinkStateDown
create log target upm ISW-down
enable log target upm ISW-down
configure log target upm ISW-down filter upmFilter severity Info



