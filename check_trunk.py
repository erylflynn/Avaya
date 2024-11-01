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

In addition, if the database was not updated in the last 5 minutes we alert as critical due to the avaya_trunk_status.py
has failed to update the information.
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
parser.add_argument("-t", default=None, dest="trunk", type=str, required=True, help="Trunk No")
args = parser.parse_args()
trunk = args.trunk

# MariaDB Host/IP, user and password
db_ip = os.getenv('db_ip')
db_user = os.getenv('db_user')
db_password = os.getenv('db_password')

current = 1
# Initiate database connection
database = create_mysql_connection(db_ip, db_user, db_password)

output = execute_query(database, trunk)
database.close()

members = output[1] + output[2] + output[3]

crit = members * .9
warn = members * .8
now = (datetime.now() - timedelta(minutes=5))

if output[4] < (datetime.now() - timedelta(minutes=5)):
    status = "CRITICAL"
    exitcode = 2
    current = 0
elif output[3] >= crit:
    status = "CRITICAL"
    exitcode = 2
elif output[3] > 0:
    status = "WARNING"
    exitcode = 1
else:
    status = "OK"
    exitcode = 0

if current == 1:
    statusmessage = "{0} - {1} Active {2} Idle {3} OOS Trunks ".format(status, output[1], output[2], output[3])
    perfmessage = 'Active={0};{1} Idle={2} OOS={3};1;{4};;'.format(output[1], members, output[2], output[3], int(crit))
else:
    statusmessage = "{0} -  Trunk status not updated in last 5 minutes".format(status)
    perfmessage = 'Active={0};{1} Idle={2} OOS={3};1;{4};;'.format(0, members, 0, 0, int(crit))


print('{0} | {1}'.format(statusmessage, perfmessage))
exit(exitcode)
