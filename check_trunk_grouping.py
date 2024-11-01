#!/usr/bin/python3
import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import argparse
from dotenv import load_dotenv
load_dotenv()
"""
This is called by the monitoring server, I use OMD/Check_MK.  Output format is for these, using legacy manual checks.

This is used for grouping logical trunk groups for monitoring and graphing.  For example when you have more channels 
than allowed in a group (255)

This is not set to alert on stale data, but you can uncomment the section below for that.  I assume you likely also will 
monitor the individual trunks and alert on them.
"""


def create_mysql_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
    except Error as err:
        print(f"Error: '{err}'")
    return connection


def execute_query(connection, trunk):
    cursor = connection.cursor()
    trunk_query = """
    SELECT *
    FROM Monitor.Trunks
    WHERE trunk_no = '{0}'
    """.format(trunk)
    try:
        cursor.execute(trunk_query)
        trunk_status = cursor.fetchone()
        return trunk_status
    except Error as err:
        print(f"Error: '{err}'")
        exit(2)


parser = argparse.ArgumentParser(description='Avaya Communication Manager check_mk trunk status check')
parser.add_argument("-t", default=None, nargs='+', dest="trunk", type=str, required=True, help="Trunk No")
args = parser.parse_args()
trunks = args.trunk

# MariaDB Host/IP, user and password
db_ip = os.getenv('db_ip')
db_user = os.getenv('db_user')
db_password = os.getenv('db_password')
members = oos = active = idle = 0
# Initiate database connection
database = create_mysql_connection(db_ip, db_user, db_password)

current = 1

for trunk in trunks:
    output = execute_query(database, trunk)
    members += output[1] + output[2] + output[3]
    active += output[1]
    idle += output[2]
    oos += output[3]
    # To alarm when stale uncomment below lines and if statements later
    # if output[4] < (datetime.now() - timedelta(minutes=5)):
    #     current = 0
database.close()

crit = members * .9
warn = members * .8
now = (datetime.now() - timedelta(minutes=5))

# To alarm when stale uncomment the below and comment the [if active >= crit:] line under it
# if current == 0:
#     status = "CRITICAL"
#     exitcode = 2
# elif active >= crit:
if active >= crit:
    status = "CRITICAL"
    exitcode = 2
elif active > warn:
    status = "WARNING"
    exitcode = 1
else:
    status = "OK"
    exitcode = 0

if not members - oos == 0:
    percent = (active/(members - oos))*100
    percent = round(percent, 2)
else:
    percent = 0

if current == 1:
    statusmessage = "{0} - {1} Active : {2} Idle : {3} OOS Trunks -- {4}% Utilization".format(status, active, idle, oos,
                                                                                          percent)
    perfmessage = 'Active={0};{1} Idle={2} OOS={3};1;{4};;'.format(active, members, idle, oos, int(crit))
else:
    statusmessage = "{0} -  Trunk status not updated in last 5 minutes".format(status)
    perfmessage = 'Active={0};{1} Idle={2} OOS={3};1;{4};;'.format(0, members, 0, 0, int(crit))


print('{0} | {1}'.format(statusmessage, perfmessage))
exit(exitcode)
