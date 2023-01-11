##########################################################
# XMC Script
#
# Author        : Luca Messori    
# Script        : Enable Netlogin on selected ports (EXOS and Extremeware switches)
# Revision      : 1.0
# Last updated  : 27.01.2022
# Purpose       : This script will enable netlogin authentication on selected ports
# Devices	    : ExtremeWare and XOS (release 15 and above)
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
# This script can be executed on switches running ExtremeWare or EXOS (release 15 and 
# above) to enable netlogin (802.1X)on selected ports.
#
# The Port list is mandatory.
# Port syntax follows the same syntax you would use on the switch: comma separated
# lists of ports or ranges are allowed. Range syntax is 1:1-5. 
# Port ranges spanning slots (e.g. 1:1-2:24) are not supported.
# 
# The service unavailable VLAN cam also be inserted and will be configured for the 
# ports belonging to the list. If the VLAN doesn't exist the script exits whith an 
# error (but netlogin is already configured in the ports).
# The service unavailable VLAN cannot be configured in ExtremeWare switches.
# UPM profiles and LLDP med cannot be configured in ExtremeWare switches.
#
#######################################################################################
#@DetailDescriptionEnd
#    @VariableFieldLabel (
#        description = "Port&#40;s&#41;",
#        type = string,
#        required = yes,
#        name = "userInput_ports",
#    )
#    @VariableFieldLabel (
#        description = "Service unavailable VLAN",
#        type = string,
#        required = no,
#        name = "userInput_servUnavailVlan",
#    )
#@MetaDataEnd
'''

#
# Imports:
#
import sys
import re
import xmclib 

print "Script start"
vlan_list = [1,2,3]
del vlan_list[:]
found = "false"
port_string = emc_vars["userInput_ports"].strip()
servUnavVlan = emc_vars["userInput_servUnavailVlan"].strip()
#IsExosSw = emc_vars["IsExos"]
#print "DEBUG - IsExos: ", IsExosSw
if emc_vars["isExos"] == "true":
    # EXOS switch
    EXOSver = emc_vars["deviceSoftwareVer"].strip()
    #print "DEBUG - Firmware: ", EXOSver
    m = re.search('^12.',EXOSver)
    if m:
        print "ERROR - Incorrect firmware version. This script can be executed on EXOS release 15 or later"
        sys.exit(1)
    cmd = 'sh netlogin dot1x | i \"802.1x ENABLED\"'
    cli_results = emc_cli.send(cmd)
    cli_output = cli_results.getOutput()
    cliout_list = cli_output.split('\n')
    #print "DEBUG - ", len(cliout_list)
    m = re.search('802.1x ENABLED',cliout_list[1])
    if m:
        print "DEBUG - Netlogin enabled "  
    else: 
        print "ERROR - Netlogin not enabled"
        sys.exit(2) 
    cmd = 'show vlan port %s ' % port_string
    cli_results = emc_cli.send(cmd)
    cli_output = cli_results.getOutput()
    cliout_list = cli_output.split('\n')
    for x in cliout_list:
        #print 'DEBUG - line: ', x
        m = re.search('Invalid input detected',x)
        if m:
            print 'ERROR - Incorrect port list syntax'
            sys.exit(4)        
        m = re.search('^nac_auth[\ ]+3500',x)
        if m:
            found = "true"
        else:
            n = re.search('^([a-zA-Z]\S+)[\ ]+([0-9]{1,4})',x)
            if n:
                #print 'DEBUG - VLAN name: ', n.group(1)
                #print 'DEBUG - VLAN tag: ', n.group(2)
                if n.group(1) != 'FAKE_EDGE_MSTP':
                    vlan_list.append(n.group(1))
    if found == "false":
        #print "DEBUG - OK"
        for i in vlan_list:
            cmd = 'configure vlan ' + i + ' del ports '+ port_string + ''
            #print 'DEBUG - cmd: ', cmd
            cli_results = emc_cli.send(cmd)
        cmd = 'enable lldp ports ' + port_string + ''   
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
        cmd = 'enable netlogin ports ' + port_string + ' dot1x mac'
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
        cmd = 'configure netlogin ports ' + port_string + ' mode mac-based-vlans'
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
        cmd = 'configure netlogin ports ' + port_string + ' no-restart'
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
        cmd = 'enable netlogin authentication service-unavailable vlan ports ' + port_string + ''
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
        cmd = 'configure netlogin authentication service-unavailable vlan ' + servUnavVlan + ' ports ' + port_string + ''
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
        cli_output = cli_results.getOutput()
        cliout_list = cli_output.split('\n')
        for y in cliout_list:
            m = re.search('Invalid input detected',x)
            if m:
                print 'WARNING - Incorrect service unavailable vlan --> NOT CONFIGURED'
                print 'Netlogin activated but the service unavailable vlan is not configured'
        cmd = 'configure upm event device-detect profile mitel-autenticato ports ' + port_string + ''
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
        cmd = 'disable cli prompting'
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
        cmd = 'save'
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
        cmd = 'enable cli prompting'
        #print 'DEBUG - cmd: ', cmd
        cli_results = emc_cli.send(cmd)
    else:
        print "Netlogin enabled at least in one port. Please remove them from the port list"
else:
    # ExtremeWare switch
    found = "false"
    port_string = emc_vars["userInput_ports"].strip(' ,')
    # Verify the syntax of the list of ports
    m = re.search('[\d\,\-]+', port_string)
    if not m:
        print "ERROR - Incorrect port list syntax - Permitted chars are: digit, hyphen and comma."  
        sys.exit(3)    
    port_string = port_string.strip(' ,')
    temp_port_list = port_string.split(',')
    temp_port_string = ""
    for myport in temp_port_list:
        #print("DEBUG - " + myport)
        m = re.search('([0-9]+)\-([0-9]+)',myport)
        if m:
            start = m.group(1)
            end = m.group(2)
            #print("DEBUG - " + start + " " + end)
            myrange = range(int(start),int(end)+1)
            for j in myrange:
                #print("DEBUG: " + str(j))
                temp_port_string = temp_port_string + str(j) + ","
        else:
            temp_port_string = temp_port_string + myport + ","
    temp_port_string = temp_port_string.strip(' ,')
    #print ("DEBUG - Port list: " + temp_port_string)   
    port_list = temp_port_string.split(',')
    for myport in port_list:
        cmd = 'show port ' + myport + ' info'
        cli_results = emc_cli.send(cmd)
        cli_output = cli_results.getOutput()
        m = re.search('out\sof\srange', cli_output)
        if m:
            print "ERROR - Incorrect port list syntax - Port " + myport + " is out of range."   
            sys.exit(3)    
    # Port list syntax OK  
    # Verify if netlogin is enabled
    cmd = 'show config'
    cli_results = emc_cli.send(cmd)
    cli_output = cli_results.getOutput()
    sw_conf = cli_output.split('\n')
    netlogin_enabled = "false"
    netlogin_vlan = "false"
    radius_srv1 = ""
    radius_srv2 = ""
    for line in sw_conf:
        m = re.search('configure\sauth\snetlogin\sradius\sprimary', line)
        if m: 
            netlogin_enabled = "true"
        m = re.search('create\svlan\s\"nac_auth\"', line)
        if m: 
            netlogin_vlan = "true"    
    if netlogin_enabled == "false" or netlogin_vlan == "false":
        print "ERROR - Netlogin not enabled - Verify the configuration - Exit"  
        sys.exit(2)
    # Netlogin altrady enabled
    for myport in port_list:
        # Verify if netlogin already enabled
        dot1x_enabled = "false"
        for line in sw_conf:
            myregexp = 'enable\snetlogin\sport\s' + myport + '\svlan\snac_auth'
            m = re.search(myregexp, line)    
            if m:
                # Netlogin already enabled on port
                print "DEBUG - Netlogin already enabled on port " + myport
                dot1x_enabled = "true"
                break
        if dot1x_enabled == "false":
            # Netlogin not yet enabled
            # Delete current VLANs from port configuration
            print "Netlogin not yet enabled on port " + myport
            cmd = 'show port ' + myport + ' info detail'
            cli_results = emc_cli.send(cmd)
            cli_output = cli_results.getOutput()
            cli_list = cli_output.split('\n')
            for cli_line in cli_list:
                #print "DEBUG - line: " + cli_line
                m = re.search('([A-Z,a-z,0-9,_-]+)\s+.+Mac-Limit.+', cli_line)
                if m:
                    # Found a VLAN to delete
                    print "DEBUG - Delete vlan " + m.group(1) + " from port " + myport
                    cmd = 'configure vlan ' + m.group(1) + ' del port ' + myport + ''
                    cli_results = emc_cli.send(cmd)
        # All the current VLANs deleted
        # Enable netlogin
        cmd = 'configure vlan nac_auth add port ' + myport + ' untag'
        cli_results = emc_cli.send(cmd)            
        cmd = 'enable netlogin port ' + myport + ' vlan nac_auth'
        cli_results = emc_cli.send(cmd)            
        cmd = 'enable netlogin port ' + myport + ' mac'
        cli_results = emc_cli.send(cmd)
        cmd = 'enable port ' + myport + ' '
        cli_results = emc_cli.send(cmd)      
    cmd = 'save config'
    #print 'DEBUG - cmd: ', cmd
    cli_results = emc_cli.send(cmd)
	
print "Script end"


