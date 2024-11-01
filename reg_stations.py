#!/usr/bin/python3
import paramiko
import time
import re
import os.path
from dotenv import load_dotenv
load_dotenv()
"""
Used to verify if a list of phones are registered.  Modify the reg_stations.txt file with stations to check, and modify
the region variable in the body of this script with the appropriate region.  You can use all but the script will take 
longer as it will parse more records.
"""


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
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    trash = ansi_escape.sub('', output.decode('utf-8'))
    return remote_conn


def list_reg(region):
    field = 'f6800ff00\n'
    termination = 't\n'
    output_final = ''
    global remote_conn
    command = "clist registered-ip-stations " + "\n"
    remote_conn.send(command)
    time.sleep(1)
    remote_conn.send(field)
    time.sleep(1)
    remote_conn.send(termination)
    time.sleep(1)
    while not output_final.endswith('t\n'):
        output = remote_conn.recv(8000)
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        output_final = output_final + ansi_escape.sub('', output.decode('utf-8'))
    log = open((os.path.dirname(__file__) + '\log.txt'), 'w')
    output_final = output_final.split('\n')
    log.write(str(output_final))
    output_final.pop(0)
    output_final.pop(0)
    output_final = [item for item in output_final if item != 'n']
    output_final.pop()
    del output_final[-1]
    return output_final


def parse_phone_list(phones):
    phone_list = []
    for extension in phones:
        phone_list.append(extension[1:])
    return phone_list


def missing_phones(file, registered):
    if not os.path.isfile(file):
        print("Sorry, reg_stations.txt does not exist.")
        exit()
    phone_list = []
    count = 0
    with open(file) as f:
        for line in f:
            line.strip()
            line = line.strip('\n')
            phone_list.append(line)
    for phone in phone_list:
        if phone not in registered:
            print(phone)
            count += 1
    print('Total phones unregistered: ' + str(count))


def missing_phones_to_file(file, registered):
    if not os.path.isfile(file):
        print("Sorry, reg_stations.txt does not exist.")
        exit()
    phone_list = []
    count = 0
    with open(file) as f:
        for line in f:
            line.strip()
            line = line.strip('\n')
            phone_list.append(line)
    f.close()
    f = open(file, 'w')
    for phone in phone_list:
        if phone not in registered:
            f.write(phone)
            f.write('\n')
            #            print(phone)
            count += 1
    print('Total phones unregistered: ' + str(count))


# Add your user name and password for CM
pbx_ip = os.getenv('pbx_ip')
pbx_user = os.getenv('pbx_user')
pbx_password = os.getenv('pbx_password')
# Change below for the region you want to target.
region = 247
# List of phones to check if registered.
list_of_phones = (os.path.dirname(__file__) + '/reg_stations.txt')

remote_conn = cm_connect(pbx_ip, pbx_user, pbx_password)
phones_reg = list_reg(region)
phones_reg = parse_phone_list(phones_reg)
missing_phones(list_of_phones, phones_reg)
# missing_phones_to_file(list_of_phones, phones_reg)
