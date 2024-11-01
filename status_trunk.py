#!/usr/bin/python3
from easysnmp import snmp_walk, exceptions
import argparse
"""
Uses SNMP to status trunks.  The bad news, at least in CM8 only the first 500 CHANNELS are exposed in the SNMP agent.
This means if you have 2 trunks, trunk 1 and trunk 2 both with 250 members, you will get no information for any other 
trunk.  This is why I was using a script using OSSI and dumping to a database.
"""



def trunk_status(community, ipaddress, trunk):
    # Trunk status OID is 1.3.6.1.4.1.6889.2.73.8.1.26.3.1.5.
    oid = '1.3.6.1.4.1.6889.2.73.8.1.26.3.1.5.' + str(trunk)
    inserviceidle = 0
    inserviceactive = 0
    oos = 0
    try:
        result = snmp_walk(community=community, ipaddress=ipaddress, oid=oid, timeout=6)
    except exceptions.SNMPTimeout:
        return False
    for item in result:
        if item[1].startswith('"in-service/idle'):
            inserviceidle += 1
        elif item[1].startswith('"in-service/active'):
            inserviceactive += 1
        elif item[1].startswith('"OOS'):
            oos += 1
        elif item[1].startswith('"out'):
            oos += 1
    return inserviceidle, inserviceactive, oos


# Use argeparser to create a list with SNMP Community, Host and Trunk number.
parser = argparse.ArgumentParser(description='Avaya Communication Manager check_mk trunk status check')
parser.add_argument("-c", default=None, dest="community", type=str, required=True, help="SNMP V2 read string")
parser.add_argument("-host", default=None, dest="host", type=str, required=True, help="Host or IP")
parser.add_argument("-t", default=None, dest="trunk", type=str, required=True, help="Trunk group number")
args = parser.parse_args()

# SNMP walk the for trunk number totalling the trunk status and assigning to variables
for i in range(3):
    try:
        inserviceidle, inserviceactive, oos = trunk_status(args.community, args.host, args.trunk)
        break
    except:
        continue

total = inserviceidle + inserviceactive + oos

# Set percentage down for critical
crit = int(.8 * total)

# Check if number of channels down and set status of check
# Any channels down will set a warning condition as a minimum
if oos >= crit:
    status = "CRITICAL"
    exitcode = 2
elif oos > 0:
    status = "WARNING"
    exitcode = 1
else:
    status = "OK"
    exitcode = 0

statusmessage = "{0} - {1} Active {2} Idle {3} OOS Trunks ".format(status, inserviceactive, inserviceidle, oos)
perfmessage = 'Active={0};{1} Idle={2} OOS={3};1;{4};;'.format(inserviceactive, total, inserviceidle, oos, crit)

# For predefined checks
# print('0 Trunk_{0} Idle={1} Active={2};{3} OOS={4};1;{5};;'.format(args.trunk, inserviceidle, inserviceactive, total, oos, crit))

# For legacy check in CHECK_MK
print('{0} | {1}'.format(statusmessage, perfmessage))
exit(exitcode)
