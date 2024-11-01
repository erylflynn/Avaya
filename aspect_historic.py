#!/usr/bin/python3

import shutil
import os
import datetime
import sys
import time

# Windows test
#src = r'C:\Users\E374789\Documents\src\\'
#dst = r'C:\Users\E374789\Documents\Test\\'
#log_dir = r'C:\Users\E374789\Documents\log\\'

src = '/home/WFMcms/incoming/'
dst = '/home/WFMcms/stream1/'
log_dir = '/home/WFMcms/logged/'
log_file = os.path.join(log_dir, "wfm_logging.txt")

if not os.path.exists(log_file):
    open(log_file, 'a').close()

files = os.listdir(src)

with open(log_file, "a") as file_object:
    now = datetime.datetime.now()
    log_string = str(now) + ' | running file copy script\n'
    file_object.write(log_string)

for file in files:
    src_file = os.path.join(src, file)
    wfm_file = os.path.join(dst, file)
    back_file = os.path.join(log_dir, file)
    if not os.path.exists(wfm_file):
        if os.path.exists(back_file):
            now = datetime.datetime.now()
            log_string = str(now) + " | " + src_file + " copy failed to destination " + back_file + " Duplicate file\n"
            with open(log_file, "a") as file_object:
                file_object.write(log_string)
        try:
            shutil.copy2(src_file, wfm_file)
            attempts = 5
            while os.path.getsize(dst + file) == 0:
                if attempts < 1:
                    break
                attempts -= 1
                os.remove(wfm_file)
                time.sleep(10)
                shutil.copy2(src_file, wfm_file)
                log_string = str(now) + " | " + wfm_file + " copied with zero file size \n"
                with open(log_file, "a") as file_object:
                    file_object.write(log_string)
            shutil.move(src_file, back_file)
            now = datetime.datetime.now()
            log_string = str(now) + " | " + src_file + " copied to " + wfm_file + "\n"
            with open(log_file, "a") as file_object:
                file_object.write(log_string)
            time.sleep(0)
        except:
            e = sys.exc_info()[0]
            log_string = str(now) + " | " + src_file + " copy failed to destination " + wfm_file + " exception error" + " | Exception error "+ e + "\n"
            with open(log_file, "a") as file_object:
                file_object.write(log_string)
            time.sleep(0)
    else:
        now = datetime.datetime.now()
        log_string = str(now) + " | " + src_file + " copy failed to destination " + wfm_file + " Duplicate file\n"
        with open(log_file, "a") as file_object:
            file_object.write(log_string)