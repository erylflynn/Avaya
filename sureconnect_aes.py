#!/usr/bin/python3
import time
import urllib.request as ul
import urllib.error
from bs4 import BeautifulSoup as soup
# python3 -m pip install BeautifulSoup4
import holidays
# python3 -m pip install holidays
import datetime


def get_url(url):
    try:
        client = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        statusmessage = '2 "SureConnect_Jetty_Status" CFcalls=0;;0|AFcalls=0'
        perfmessage = "CallerFirst Calls = 0, AgentFirst Calls = 0, Jetty is Down, Exception error {0}".format(e)
        print('{0} {1}'.format(statusmessage, perfmessage))
        exit(1)
    htmldata = client.read()
    client.close()
    pagesoup = soup(htmldata, "html.parser")
    table = pagesoup.find_all(width='250')
    table = table[2:]
    call_list = pagesoup.find_all(text=True)
    return call_list, table


def parse_table(table):
    true = false = 0
    for row in table:
        row = str(row)
        if 'true' in row:
            true += 1
        elif 'false' in row:
            false += 1
    if true > 0 and false == 0:
        return "Up"
    else:
        return "Down"


def get_call_count(page):
    total_calls = 0
    for i in page:
        text_line = str(i)
        if text_line.__contains__('COUNT'):
            text_line = text_line.strip()
            calls = int(text_line.split()[1])
            total_calls += calls
    return total_calls


def set_exit_code(AES_state, callerfirst):
    exitcodes = 0
    us_holiday = holidays.US()
    if time.localtime().tm_hour > 16 or time.localtime().tm_hour < 7:
        exitcodes = 0
    elif datetime.datetime.today().weekday() > 4:
        exitcodes = 0
    elif datetime.datetime.now().strftime("%d-%m-%Y") in us_holiday:
        exitcodes = 0
#    elif callerfirst == 0:
#        exitcodes += 1
    if AES_state == "Down":
        exitcodes += 1
    return exitcodes


def getCBrequests(url):
    try:
        client = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        statusmessage = '1 "SureConnect_Jetty_Status" CFcalls=0;;0|AFcalls=0|CBrequests=0'
        perfmessage = "CallerFirst Calls = 0, AgentFirst Calls = 0, Callback Requests = 0, Jetty is Down, Exception error {0}".format(e)
        print('{0} {1}'.format(statusmessage, perfmessage))
        exit(1)
    htmldata = client.read()
    client.close()
    pagesoup = soup(htmldata, "html.parser")
    tables = pagesoup.find_all('tr')
    calls = len(tables) - 1
    return calls


"""
Modify the lower URLs to include the hostname or IP of your INI(Interactive Northwest) SureConnect application servers.
"""
webpage_c = 'http://HOSTNAME OR IP:9092/CallerFirstDirector/'
webpage_a = 'http://HOSTNAME OR IP:9092/AgentFirstDirectorCTI/'
webpage_cb = 'http://HOSTNAME OR IP:9092/DialingEngineContainer/pendingcalls.jsp'

read_pagea, read_table = get_url(webpage_a)
read_pagec, read_table = get_url(webpage_c)
callerfirst_call_count = get_call_count(read_pagec)
agentfirst_call_count = get_call_count(read_pagea)

AES_connect = parse_table(read_table)
exitcode = set_exit_code(AES_connect, callerfirst_call_count)
total_calls = callerfirst_call_count + agentfirst_call_count

cb_requests = getCBrequests(webpage_cb)

statusmessage = '{0} "SureConnect_Jetty_Status" CFcalls={1};;0|AFcalls={2}|CBrequests={3}'.format(exitcode, callerfirst_call_count, agentfirst_call_count, cb_requests)

perfmessage = "CallerFirst Calls = {0}, AgentFirst Calls = {1}, Callback Requests = {2}, Jetty is {3}".format(callerfirst_call_count, agentfirst_call_count, cb_requests, AES_connect)

print('{0} {1}'.format(statusmessage, perfmessage))
exit(exitcode)
