#!/usr/bin/python3
import paramiko
import time
import re
import mysql.connector
from mysql.connector import Error
import os.path
from icecream import ic
from dotenv import load_dotenv
load_dotenv()
"""
This will be ran at startup on host machine.  This should be ran on same host as the monitoring engine and the MYSQL 
Database.  If not you will need to secure and enable remote access to the database.
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


def execute_query(connection, inserviceidle, inserviceactive, oos, trunk):
    cursor = connection.cursor()
    trunk_query = """
    INSERT INTO Monitor.Trunks (trunk_no, in_use, idle, oos) 
    VALUES ('{0}','{1}','{2}','{3}')
    ON DUPLICATE KEY UPDATE
    in_use = '{1}', idle = '{2}', oos = '{3}', updated = NOW()
    """.format(trunk, inserviceactive, inserviceidle, oos)
    try:
        cursor.execute(trunk_query)
        connection.commit()
    except Error as err:
        print(f"Error: '{err}'")


def try_status_trunk(trunk_no, connection):
    field = 'f0003ff00\n'
    termination = 't\n'
    output_final = ''
    global remote_conn
    command = "cstatus trunk " + str(trunk_no) + "\n"
    remote_conn.send(command)
    time.sleep(.5)
    remote_conn.send(field)
    time.sleep(.5)
    remote_conn.send(termination)
    # check for termination character sent at end of output.  This allows us to not require long sleeps
    # to capture delayed data from command being issued.
    while not output_final.endswith('t\n'):
        output = remote_conn.recv(8000)
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        output_final = output_final + ansi_escape.sub('', output.decode('utf-8'))
        print(output_final)
    if 'All maintenance resources busy' in output_final:
        return 1
    output_final = output_final.split('\n')
    output_final.pop(0)
    output_final.pop(0)
    output_final = [item for item in output_final if item != 'n']
    output_final.pop()
    del output_final[-1]
    return output_final


def status_trunk(trunk_no, connection):
    maint_busy = 0
    while maint_busy == 0:
        try:
            trunk_status = try_status_trunk(int(trunk), connection)
        except:
            time.sleep(1)
            try:
                print('Trying to reconnect')
                connection = cm_connect(pbx_ip, pbx_user, pbx_password)
            except:
                continue
            continue
        if trunk_status != 1:
            maint_busy = 1
    return trunk_status, connection


def parse_trunk_results(trunk_list):
    inserviceidle = inserviceactive = oos = 0
    for line in trunk_list:
        if line.startswith('din-service/idle'):
            inserviceidle += 1
        elif line.startswith('din-service/active'):
            inserviceactive += 1
        elif line.startswith('dOOS'):
            oos += 1
        elif line.startswith('dout'):
            oos += 1
        elif line.startswith('dpending-busyout'):
            inserviceactive += 1
        else:
            oos += 1
    return inserviceidle, inserviceactive, oos


def cm_connect(host, user, passwd):
    remote_conn_pre = paramiko.SSHClient()
    remote_conn_pre.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    remote_conn_pre.connect(host, username=user, port=5022, password=passwd, look_for_keys=False, allow_agent=False)
    remote_conn = remote_conn_pre.invoke_shell()
    time.sleep(1)
    # Terminal type reqeuest OSSI for machine interfaces and OSSIZ for super user
    remote_conn.send("ossiz\n")
    time.sleep(2)
    output = remote_conn.recv(5000)
    # print(output)
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    trash = ansi_escape.sub('', output.decode('utf-8'))
    return remote_conn


# Icecream for debugging
ic.disable()

# Trunks listed in comma separated format.  Only reads first line, ignores 2nd on.
configfile = (os.path.dirname(__file__) + '/avaya_trunk_status.conf')
# create a file just named stop in the root directory to stop the application
stopfile = (os.path.dirname(__file__) + '/stop')
# create a file just named disable in the root directory and the application will not start up, but immediately exit.
disable = (os.path.dirname(__file__) + '/disable')

# check for flag file to prevent start and running of application
if os.path.isfile(disable):
    exit(0)

# global remote_conn
# global database
# PBX Host/IP, user and password
pbx_ip = os.getenv('pbx_ip')
pbx_user = os.getenv('pbx_user')
pbx_password = os.getenv('pbx_password')

# MariaDB Host/IP, user and password
db_ip = os.getenv('db_ip')
db_user = os.getenv('db_user')
db_password = os.getenv('db_password')

# Read configuration file, exit out if it does not exist.
if not os.path.isfile(configfile):
    print("Config file does not exist.")
    exit()
else:
    with open(configfile)as f:
        content = f.readline().split(',')

#fpid = os.fork()
#if fpid != 0:
#    sys.exit(0)

# Initiate database connection
database = create_mysql_connection(db_ip, db_user, db_password)

# Initialize PBX connection
remote_conn = cm_connect(pbx_ip, pbx_user, pbx_password)



# Check for stop file and break loop if exists
while not os.path.isfile(stopfile):
    for trunk in content:
        if os.path.isfile(disable):
            exit(0)
        trunk = trunk.strip()
        output, remote_conn = status_trunk(int(trunk), remote_conn)
        inserviceidle, inserviceactive, oos = parse_trunk_results(output)
        print(trunk)
        print("OOS = " + str(oos))
        print("Inservice Active = " + str(inserviceactive))
        print('Inservice Idle = ' + str(inserviceidle))
        execute_query(database, inserviceidle, inserviceactive, oos, trunk)

os.remove(stopfile)
remote_conn.close
