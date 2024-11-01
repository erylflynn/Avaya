#!/usr/bin/python3
import time
#from snmp_cmds import snmpwalk, exceptions
from easysnmp import snmp_walk, exceptions
import argparse


def poll_oid(oid):
    i = 0
    while i < 4:
        try:
            walk = snmp_walk(community=community, ipaddress=ipaddress, oid=oid, timeout=6)
            success = True
            walk = split_walk(walk)
            break
        except exceptions.SNMPTimeout:
            success = False
            time.sleep(1)
    if success:
        return walk
    else:
        return False


def split_walk(walk):
    result = []
    for item in walk:
        result.append(item[1])
    return result


def total_channels(walk):
    total = 0
    for core in walk:
        total += int(core)
    return total


def dsp_status_result(walk):
    total_oos = 0
    for core in walk:
        if core == 3:
            total_oos += 1
    return total_oos


def dsp_admin_result(walk):
    total_oos = 0
    for core in walk:
        if core != '2':
            if core != '255':
                total_oos += 1
    return total_oos


# Use argeparser to create a list with SNMP Community and Host.
parser = argparse.ArgumentParser(description='Avaya G450 Gatewat check_mk DSP status check')
parser.add_argument("-c", default=None, dest="community", type=str, required=True, help="SNMP V2 read string")
parser.add_argument("-host", default=None, dest="host", type=str, required=True, help="Host or IP")
args = parser.parse_args()

# Declare and assign variables
ipaddress = args.host
community = args.community
core_oos = 0
# List of DSP bank channels per core
total_dsp_oid = '.1.3.6.1.4.1.6889.2.9.1.4.6.1.2'

# List of DSP channels in use per bank and core
in_use_dsp_oid = '.1.3.6.1.4.1.6889.2.9.1.4.6.1.3'

# List of DSP Core status
# values:  INTEGER {idle(1), inUse(2), fault(3) }
dsp_status_oid = '.1.3.6.1.4.1.6889.2.9.1.4.6.1.5'

# List of DSP COre Admin State
# Values:  INTEGER {busy-out(1), release(2), camp-on(3), unknown(255) }
dsp_admin_state_oid = '.1.3.6.1.4.1.6889.2.9.1.4.6.1.4'

# SNMP Poll our OIDS
total_dsp_list = poll_oid(total_dsp_oid)
in_use_dsp_list = poll_oid(in_use_dsp_oid)
dsp_status_list = poll_oid(dsp_status_oid)
dsp_admin_state_list = poll_oid(dsp_admin_state_oid)

if not total_dsp_list:
    print('OK - SNMP Polling failed  | Active=0;1;2;3 Idle=0 ')
    exit(0)
elif not in_use_dsp_list:
    print('OK - SNMP Polling failed  | Active=0;1;2;3 Idle=0 ')
    exit(0)
elif not dsp_status_list:
    print('OK - SNMP Polling failed  | Active=0;1;2;3 Idle=0 ')
    exit(0)
elif not dsp_admin_state_list:
    print('OK - SNMP Polling failed  | Active=0;1;2;3 Idle=0 ')
    exit(0)

# Total and resolve the SNMP results
total_dsp = total_channels(total_dsp_list)
in_use_dsp = total_channels(in_use_dsp_list)
dsp_status = dsp_status_result(dsp_status_list)
dsp_admin_state = dsp_admin_result(dsp_admin_state_list)
idle_dsp = total_dsp - in_use_dsp

if dsp_status > dsp_admin_state:
    core_oos = dsp_status
else:
    core_oos = dsp_admin_state

crit = total_dsp * .9
warn = total_dsp * .7

if core_oos > 0:
    status = 'CRITICAL'
    exitcode = 2
elif in_use_dsp > crit:
    status = 'CRITICAL'
    exitcode = 2
elif in_use_dsp > warn:
    status = 'WARNING'
    exitcode = 1
else:
    status = 'OK'
    exitcode = 0

if core_oos > 0:
    statusmessage = "{0} - 1 or more DSP Cores OOS - {1} Active DSPs, {2} Idle DSPs, DSP Walk {3} ".format(status, in_use_dsp, idle_dsp, dsp_admin_state)
else:
    statusmessage = "{0} - {1} Active DSPs, {2} Idle DSPs, DSP Walk {3} ".format(status, in_use_dsp, idle_dsp, dsp_admin_state)


perfmessage = 'Active={0};{1};{2};{3} Idle={4} '.format(in_use_dsp, int(warn), int(crit), total_dsp, idle_dsp)

print('{0} | {1}'.format(statusmessage, perfmessage))
exit(exitcode)
