#!/usr/bin/env python
import exsh
import sys
import os
import argparse
import socket
import re


lista_mac = [1,2,3]
lista_vlan=[1,2,3]
lista_tagg=[1,2,3]
lista_user = [1,2,3]
del lista_mac[:]
del lista_vlan[:]
del lista_tagg[:]
del lista_user[:]

# Insert netlogin client data in three different lists
# For each netlogin client:
# lista_mac contains MAC address
# lista_vlan contains VLAN names
# lista_tagg contains info about vlan taging (tagged or untagged)

cmd = 'show fdb netlogin all'
#cliout.setSessionTimeout(120)
cliout = exsh.clicmd(cmd, capture=True)
cliout_list = cliout.split('\n')
for x in cliout_list:
    m = re.search('(([0-9a-f]{2}[:-]){5}([0-9a-f]{2}))',x)
    if m:
        n = x.split()
        v = n[1].split('(')
        if m and v:
            # n[-1] --> switch port; v[0] --> VLAN name
            cmd = 'show port %s info detail | include %s' % (n[-1], v[0])
            cliout = exsh.clicmd(cmd, capture=True)
            cliout_list = cliout.split('\n')
            if re.search('Internal',cliout_list[0]):
                t = "untagged"
            elif re.search('802.1Q',cliout_list[0]):
                t = "tagged"
            else:
                t = ""
            if t == "tagged" or t == "untagged":
                lista_mac.append(m.group(0)) # MAC address
                lista_vlan.append(v[0]) # VLAN name
                lista_tagg.append(t) # Switch port

#print 'Number of mac addresses = ', len(lista_mac)


# Delete saved netlogin local users
print 'Users: '
cmd = 'show netlogin local-users'
cliout = exsh.clicmd(cmd, capture=True)
cliout_list = cliout.split('\n')
for x in cliout_list:
    m = re.search('([0-9A-F]{12})',x)
    if m:
        lista_user.append(m.group(0))
        print "Delete local-user" + m.group(0)
        cmd = 'delete netlogin local-user %s' % (m.group(0))
        exsh.clicmd(cmd, capture=False)

# Create new netlogin local users
i = 0
for y in lista_mac:
    print "%d) Add local-user %s vlan %s" % (i, y, lista_vlan[i])
    mac_no_duepunti = y.replace(":","")
    mac_uppercase = mac_no_duepunti.upper()
    mac_oui = mac_uppercase[0:6]
    cmd = 'create netlogin local-user %s %s vlan-vsa %s %s' % (mac_uppercase , mac_uppercase, lista_tagg[i], lista_vlan[i])
    exsh.clicmd(cmd, capture=False)
    i = i + 1

