##########################################################
# XMC Script
#
# Author        : Luca Messori    
# Script        : Enable Netlogin on switch
# Revision      : 1.0
# Last updated  : 25.01.2022
# Purpose       : This script will enable 802.1X authentication in Extreme Neworks switches
# Devices	    : ExtremeWare and XOS (15.0.0+)
#
##########################################################
#
# XMC Metadata
#
'''
#@MetaDataStart
#@DetailDescriptionStart
######################################################################################
# 
# This script can be executed on switches running ExtremeWare or EXOS (version 15 or  
# following) to globally enable netlogin (802.1X).
#
# It create the global configurations nedeed by netlogin.
#
# The parameters that identify the Radius server IPs and the Voice VLAN are mandatory.
# The Voice VLAN parameter will not be used in ExtremeWare devices.
# The Radius servers IP are pre-compiled. They can be modified but cannot be deleted.
# The shared secret is not mandatory; there is a predefined value that can be used.
#
#######################################################################################
#@DetailDescriptionEnd
#    @VariableFieldLabel (
#        description = "First Radius server ",
#        type = string,
#        required = yes,
#        name = "userInput_Srv1",
#        value = "1.1.1.1",
#    )
#    @VariableFieldLabel (
#        description = "Second Radius server ",
#        type = string,
#        required = yes,
#        name = "userInput_Srv2",
#        value = "1.1.1.2",
#    )
#    @VariableFieldLabel (
#        description = "Shared secret",
#        type = string,
#        required = no,
#        name = "userInput_SharedSec",
#    )
#@MetaDataEnd
'''

#
# Imports:
#
import sys
import re
from xmclib import emc_vars

# Default values (must be modified):"
DefSharedSec = "mypsk"
XmcIp = "2.2.2.2"
# END of Default values

print "Script start"
found = "false"
RadSrv1 = emc_vars["userInput_Srv1"].strip()
RadSrv2 = emc_vars["userInput_Srv2"].strip()
SharedSec = emc_vars["userInput_SharedSec"].strip()
deviceIp = emc_vars["deviceIP"] 
#print "DEBUG - deviceIP: ", deviceIp

IsEXOSdev = emc_vars["isExos"].strip()
#print "DEBUG - Is EXOS? : ", IsEXOSdev
if IsEXOSdev == "true":
    # EXOS Devices
    #print "DEBUG - EXOS"
    EXOSver = emc_vars["deviceSoftwareVer"].strip()
    #print "DEBUG - Firmware: ", EXOSver
    m = re.search('^12.',EXOSver)
    if m:
        print "ERROR - Incorrect EXOS firmware version. This script can be executed on EXOS release 15 or later"
        sys.exit(1)
    
    cmd = 'sh netlogin dot1x | i \"802.1x ENABLED\"'
    cli_results = emc_cli.send(cmd)
    cli_output = cli_results.getOutput()
    cliout_list = cli_output.split('\n')
    #rint "DEBUG - ", len(cliout_list)
    m = re.search('802.1x ENABLED', cliout_list[1])
    if m:
        print "ERROR - Netlogin already enabled "  
        sys.exit(2)
    else: 
        print "DEBUG - Netlogin is going to be enabled"
    
    m = re.search('^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$',RadSrv1)
    if m:
        print "DEBUG - IP of the first Radius server: OK"  
    else: 
        print "ERROR - IP of the first Radius server: KO"
        sys.exit(3)
    
    m = re.search('^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$',RadSrv2)
    if m:
        print "DEBUG - IP of the second Radius server: OK"  
    else: 
        print "ERROR - IP of the second Radius server: KO"
        sys.exit(3)
        
    if len(SharedSec.strip()):
        print "DEBUG - shared secret not null"
    else:
        SharedSec =  DefSharedSec
    #print "DEBUG - Radius shared secret: ", SharedSec
                    
    # All parameters are OK
    # let start the configuration
    cmd = 'disable cli prompting'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    #Radius
    cmd = 'configure radius netlogin primary server ' + RadSrv1 + ' 1812 client-ip ' + deviceIp + ' vr VR-Default'   
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure radius netlogin primary shared-secret ' + SharedSec + ''
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure radius netlogin secondary server ' + RadSrv2 + ' 1812 client-ip ' + deviceIp + ' vr VR-Default'   
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure radius netlogin secondary shared-secret ' + SharedSec + ''
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure radius-accounting netlogin primary server ' + RadSrv1 + ' 1813 client-ip ' + deviceIp + ' vr VR-Default'   
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure radius-accounting netlogin primary shared-secret ' + SharedSec + ''
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure radius-accounting netlogin secondary server ' + RadSrv2 + ' 1813 client-ip ' + deviceIp + ' vr VR-Default'   
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure radius-accounting netlogin secondary shared-secret ' + SharedSec + ''
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'enable radius-accounting netlogin'   
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'enable radius netlogin'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    # Netlogin
    cmd = 'create vlan nac_auth'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure vlan nac_auth tag 3500'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure netlogin vlan nac_auth'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'enable netlogin dot1x mac'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'configure netlogin add mac-list ff:ff:ff:ff:ff:ff 48'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)

    cmd = 'save config'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
    
    cmd = 'enable cli prompting'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
else:
    # ExtremeWare devices
    print "DEBUG - Start ExtremeWare configuration"
    cmd = 'show configuration'
    cli_results = emc_cli.send(cmd)
    cli_output = cli_results.getOutput()
    cliout_list = cli_output.split('\n')
    #print "DEBUG - ", cli_output
    netlogin_enabled = "false"
    radius_configured = "false"
    netman_configured = "false"
    radius_srv1 = ""
    radius_srv2 = ""
    for line in cliout_list:
        m = re.search('enable\snetlogin\sport\s', line)
        if m: 
            netlogin_enabled = "true"
        m = re.search('configure\sradius\sprimary\sserver\s([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\s.+', line)
        if m:
            radius_configured = "true"
            radius_srv1 = m.group(1)
        m = re.search('configure\sradius\ssecondary\sserver\s([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\s.+', line)
        if m:
            radius_configured = "true"
            radius_srv2 = m.group(1)
        m = re.search('create\saccount\sadmin\s\"netman\"', line)  
        if m:
            netman_configured = "true"
    if netlogin_enabled == "true": 
        print "ERROR - Netlogin already enabled - Exit"  
        sys.exit(2)
    else:
        print "DEBUG - Netlogin not enabled, enabling it"
        if netman_configured == "false":
            print "DEBUG - create account netman"
            cmd = 'create account admin netman carisbo'
            cli_results = emc_cli.send(cmd)
        print "DEBUG - modify auth mgmt-access"
        cmd = 'configure auth mgmt-access local'
        cli_results = emc_cli.send(cmd)
        # We configure Radius servers and netlogin
        if radius_srv2:
            print "DEBUG - unconfigure radius server secondary"
            cmd = 'unconfigure radius server secondary ' + radius_srv2 + ''
            cli_results = emc_cli.send(cmd)
        if radius_srv1:
            print "DEBUG - unconfigure radius server primary"
            cmd = 'unconfigure radius server primary ' + radius_srv1 + ''
            cli_results = emc_cli.send(cmd)
        if len(SharedSec.strip()):
            print "DEBUG - shared secret is not null"
        else:
            print "DEBUG - shared secret is null, use default"
            SharedSec =  DefSharedSec
        cmd = 'configure radius secondary shared-secret ' + SharedSec + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'configure radius primary shared-secret ' + SharedSec + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'configure radius secondary server ' + RadSrv2 + ' 1812 client-ip ' + deviceIp + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'configure radius primary server ' + RadSrv1 + ' 1812 client-ip ' + deviceIp + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'configure radius-accounting secondary shared-secret ' + SharedSec + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'configure radius-accounting primary shared-secret ' + SharedSec + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'configure radius-accounting secondary server ' + RadSrv2 + ' 1813 client-ip ' + deviceIp + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'configure radius-accounting primary server ' + RadSrv1 + ' 1813 client-ip ' + deviceIp + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'enable radius-accounting'   
        cli_results = emc_cli.send(cmd)
        cmd = 'enable radius'
        cli_results = emc_cli.send(cmd)
        cmd = 'configure auth mgmt-access local'
        cli_results = emc_cli.send(cmd)
        cmd = 'configure auth netlogin radius primary ' + RadSrv1 + ' secondary ' + RadSrv2 + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'configure auth netlogin radius-accounting primary ' + RadSrv1 + ' secondary ' + RadSrv2 + ''
        cli_results = emc_cli.send(cmd)
        cmd = 'create vlan nac_auth'
        cli_results = emc_cli.send(cmd)
        cmd = 'configure vlan nac_auth tag 3500'
        cli_results = emc_cli.send(cmd) 
        cmd = 'configure netlogin mac auth-retry-count 3'
        cli_results = emc_cli.send(cmd)
        cmd = 'configure netlogin mac reauth-period 1800'
        cli_results = emc_cli.send(cmd)
        cmd = 'configure netlogin mac-address default'
        cli_results = emc_cli.send(cmd)
        cmd = 'configure netlogin dot1x timers supp-resp-timeout 60'
        cli_results = emc_cli.send(cmd) 
        cmd = 'enable netlogin dot1x'
        cli_results = emc_cli.send(cmd)        
        cmd = 'enable netlogin mac'
        cli_results = emc_cli.send(cmd)               
        cmd = 'save config'
        cli_results = emc_cli.send(cmd)

print "Script end"