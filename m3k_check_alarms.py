#!/usr/bin/python
__author__ = 'bpeckin'
import netsnmp
import sys, getopt

CRIT = 0
MAJOR = 0
MINOR = 0
WARN = 0
UNKNOWN = 0
STATE_OK = 0
STATE_WARNING = 1
STATE_CRITICAL = 2
STATE_UNKNOWN = 3
RETURN_CODE = 0
HOST = ""
COMMUNITY = ""
#Variable used for loops, reset before use
counter = 0

def usage():
    print('Please include both -H followed by host IP address and -C followed by SNMP v2 Community string')
    sys.exit()

try:
    options, remainder = getopt.getopt(sys.argv[1:], 'H:C:')
except getopt.GetoptError as err:
    # print help information and exit:
    print(err)
    usage()

for opt, arg in options:
    if opt == '-H':
        HOST = arg
    elif opt == '-C':
        COMMUNITY = arg
    else:
        usage()
        sys.exit()

if HOST == "" or COMMUNITY == "":
    usage()

test_oid = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.2.1.1.1'))
test_res = netsnmp.snmpwalk(test_oid, Version=2, DestHost=HOST, Community=COMMUNITY)
counter = 0
for var in test_oid:
    counter += 1
if counter == 0:
    RETURN_CODE = STATE_CRITICAL
    print("SNMP Reply time out")
    sys.exit(RETURN_CODE)


desc_oid = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.5003.11.1.1.1.1.6'))
sev_oid = netsnmp.VarList(netsnmp.Varbind('.1.3.6.1.4.1.5003.11.1.1.1.1.8'))

desc_res = netsnmp.snmpwalk(desc_oid, Version=2, DestHost=HOST, Community=COMMUNITY)
sev_res = netsnmp.snmpwalk(sev_oid, Version=2, DestHost=HOST, Community=COMMUNITY)

counter = 0
for var in desc_oid:
    counter += 1
if counter == 0:
    RETURN_CODE = STATE_OK
    print("OK")
    sys.exit(RETURN_CODE)

alarmCount = len(desc_res)

if alarmCount == 1:
    alarmCount += 1

alarmList = [[0 for i in range(2)] for j in range(alarmCount)]

if alarmCount == 1:
    alarmList[alarmCount - 1][0] = ""
    alarmList[alarmCount - 1][1] = ""


#Resetting counter
counter = 0

for var in desc_oid:
        alarmList[counter][1] = ": "+var.val+"]"
        counter += 1

#Resetting counter again
counter = 0

for var in sev_oid:
    if var.val == "4":
        MAJOR += 1
        sev = ". . .[Major"
        alarmList[counter][0] = sev
    else:
        if var.val == "5":
            CRIT += 1
            sev = ". . .[Critical"
            alarmList[counter][0] = sev
        else:
            if var.val == "3":
                MINOR += 1
                sev = ". . .[Minor"
                alarmList[counter][0] = sev
            else:
                if var.val == "2":
                    WARN += 1
                    sev = ". . .[Warning"
                    alarmList[counter][0] = sev
                else:
                    if var.val == "1":
                        UNKNOWN += 1
                        sev = ". . .[Unknown"
                        alarmList[counter][0] = sev
    counter += 1

if CRIT > 0:
    RETURN_CODE = STATE_CRITICAL
    RETURN_STATE = "CRIT"
elif MAJOR > 0:
    RETURN_CODE = STATE_CRITICAL
    RETURN_STATE = "CRIT"
elif MINOR > 0:
    RETURN_CODE = STATE_CRITICAL
    RETURN_STATE = "CRIT"
elif WARN > 0:
    RETURN_CODE = STATE_WARNING
    RETURN_STATE = "WARN"
elif UNKNOWN > 0:
    RETURN_CODE = STATE_UNKNOWN
    RETURN_STATE = "UNKNOWN"
else:
    RETURN_CODE = STATE_OK
    RETURN_STATE = "OK"

OUTPUT = ("Critical: "+str(CRIT)+", Major: "+str(MAJOR)+", Minor: "+str(MINOR)+", Warning: "+str(WARN)+", Unknown: "+str(UNKNOWN))

#Resetting counter again
counter = 0

for var in alarmList:
        OUTPUT += alarmList[counter][0] + alarmList[counter][1]
        counter += 1


print(RETURN_STATE+" - "+OUTPUT)

sys.exit(RETURN_CODE)
