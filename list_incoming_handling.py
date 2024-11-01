#!/usr/bin/python3
import os

import paramiko
import time
import re
import openpyxl
from dotenv import load_dotenv
load_dotenv()


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


def parse_list_usage(raw_list, extension):
    clean_list = []
    for item in raw_list:
        if item.startswith('d'):
            ext_type = item[1:].split("\t")
            ext_type.insert(0, extension)
            clean_list.append(ext_type)
    return clean_list


def display_incoming(trunk):
    field1 = 5570305
    field2 = 5701377
    termination = 't\n'
    output_final = ''
    global remote_conn
    command = "cdisplay inc-call-handling-trmt trunk-group " + str(trunk) + "\n"
    remote_conn.send(command)
    i = 0
    while i < 540:
        i += 1
        hex1 = hex(field1)
        hex2 = hex(field2)
        hex1 = 'f00' + hex1[2:]
        hex2 = 'f00' + hex2[2:]
        hex_field1 = hex1 + "\n"
        hex_field2 = hex2 + "\n"
        remote_conn.send(hex_field1)
        remote_conn.send(hex_field2)
        field1 += 1
        field2 += 1
    remote_conn.send(termination)
    time.sleep(.5)
    while not output_final.endswith('t\n'):
        output = remote_conn.recv(8000)
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        output_final = output_final + ansi_escape.sub('', output.decode('utf-8'))
    output_final = output_final.split('\n')
    return output_final


# Add your user name and password for CM
pbx_ip = os.getenv('pbx_ip')
pbx_user = os.getenv('pbx_user')
pbx_password = os.getenv('pbx_password')
wb = openpyxl.Workbook()
sheet = wb.active

remote_conn = cm_connect(pbx_ip, pbx_user, pbx_password)

print(display_incoming(4))
