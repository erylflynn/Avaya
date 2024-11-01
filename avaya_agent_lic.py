#!/usr/bin/python3
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
        except exceptions.EasySNMPTimeoutError:
            success = False
    if success:
        return walk
    else:
        return False


def split_walk(walk):
    result = []
    for item in walk:
        result.append(item[1])
    return result


# Use argeparser to create a list with SNMP Community and Host.
parser = argparse.ArgumentParser(description='Avaya Communication Manager check_mk One-X License check')
parser.add_argument("-c", default=None, dest="community", type=str, required=True, help="SNMP V2 read string")
parser.add_argument("-host", default=None, dest="host", type=str, required=True, help="Host or IP")
args = parser.parse_args()

# Declare and assign variables
ipaddress = args.host
community = args.community

# One-X Agent License in use
agent_lic_used_oid = '.1.3.6.1.4.1.6889.2.73.8.1.23.1.1.4.8.73.80.95.65.103.101.110.116'

# One-X Agnet License Available
agent_lic_available_oid = '.1.3.6.1.4.1.6889.2.73.8.1.23.1.1.5.8.73.80.95.65.103.101.110.116'

# One-X Agent License Total
agent_lic_total_oid = '.1.3.6.1.4.1.6889.2.73.8.1.23.1.1.6.8.73.80.95.65.103.101.110.116'

# SNMP Poll our OIDS
agent_lic_used = poll_oid(agent_lic_used_oid)
agent_lic_available = poll_oid(agent_lic_available_oid)
agent_lic_total = poll_oid(agent_lic_total_oid)

agent_lic_used = int(agent_lic_used[0])
agent_lic_available = int(agent_lic_available[0])
agent_lic_total = int(agent_lic_total[0])

crit = .9 * agent_lic_total
warn = .8 * agent_lic_total

if not agent_lic_used:
    print('OK - SNMP Polling failed  | Active=0;1;2;3 Idle=0 ')
    exit(0)
elif not agent_lic_available:
    print('OK - SNMP Polling failed  | Active=0;1;2;3 Idle=0 ')
    exit(0)
elif not agent_lic_total:
    print('OK - SNMP Polling failed  | Active=0;1;2;3 Idle=0 ')
    exit(0)


if agent_lic_used > crit:
    status = 'CRITICAL'
    exitcode = 2
elif agent_lic_used > warn:
    status = 'WARNING'
    exitcode = 1
else:
    status = 'OK'
    exitcode = 0

statusmessage = "{0} - {1} Agent Lic Used, {2} Available Agent Licenses ".format(status, agent_lic_used, agent_lic_available, )
perfmessage = 'Active={0};{1};{2};{3} Idle={4} '.format(agent_lic_used, int(warn), int(crit), agent_lic_total, agent_lic_available)

print('{0} | {1}'.format(statusmessage, perfmessage))
exit(exitcode)
