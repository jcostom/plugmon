#!/usr/bin/env python3

import os
import time
import requests
import random
import hashlib
from pyvesync_v2 import VeSync

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
MD5PASSWORD = hashlib.md5(PASSWORD.encode('utf-8')).hexdigest()
TZ = os.getenv('TZ', 'America/New_York')
DEVNAME = os.getenv('DEVNAME')
OFFPOWER = float(os.getenv('OFFPOWER', 1.2))
ONPOWER = float(os.getenv('ONPOWER', 3.0))
IFTTTKEY = os.getenv('IFTTTKEY')
IFTTTWEBHOOK = os.getenv('IFTTTWEBHOOK')
INTERVAL = os.getenv('INTERVAL', 300)
TRACEID = random.uniform(0, 1)

VER = 'plugmon.py v1.5'

def findDeviceID(deviceName, email, md5pass, tz, traceid):
    # First fetch token & accountID
    headers = { 'content-type': 'application/json' }
    body = {
        'accountID': '',
        'account': email,
        'password': md5pass,
        'timeZone': tz,
        'token': ''
    }
    url = 'https://smartapi.vesync.com/vold/user/login'
    r = requests.post(url, headers=headers, json=body)
    ACCOUNTID = r.json()['accountID']
    TOKEN = r.json()['tk']

    # Next collect list of devices
    headers = {
      'tk': TOKEN,
      'accountid': ACCOUNTID,
      'content-type': 'application/json',
      'tz': tz,
      'user-agent': 'HappyFunBall'
    }
    body = {
        'acceptLanguage': 'en',
        'accountID': ACCOUNTID,
        'appVersion': '1.1',
        'method': 'devices',
        'pageNo': '1',
        'pageSize': '1000',
        'phoneBrand': 'HappyFunBall',
        'phoneOS': 'HappyFunOS',
        'timeZone': tz,
        'token': TOKEN,
        'traceId': traceid
    }
    url = 'https://smartapi.vesync.com/cloud/v2/deviceManaged/devices'
    r = requests.post(url, headers=headers, json=body)
    list = r.json()['result']['list']

    for i in range(len(list)):
        if list[i]['deviceName'] == devName:
            devID = i
            break

    return(devID)

def triggerWebHook():
    webHookURL = "/".join(
        ("https://maker.ifttt.com/trigger",
        IFTTTWEBHOOK,
        "with/key",
        IFTTTKEY)
    )
    headers = {'User-Agent': VER }
    r = requests.get(webHookURL, headers=headers)
    print(time.strftime("[%d %b %Y %H:%M:%S %Z]", time.localtime()) + " IFTTT Response: {}".format(r.text))

def main():
    DEVID = findDeviceID(DEVNAME, EMAIL, MD5PASSWORD, TZ, TRACEID)

    # Now, get down to business, finally.
    # Hey VeSync gang - give us a way to directly access
    # info by UUID or CID fields!

    manager = VeSync(EMAIL, PASSWORD, TZ)
    manager.login()
    manager.update()
    mysw = manager.outlets[DEVID]
    IS_RUNNING = 0

    while True:    
        manager.update()
        manager.update_energy()
        mysw_power = float(mysw.details.get('power',0))
        if IS_RUNNING == 0:
            if mysw_power > ONPOWER:
                print(time.strftime("[%d %b %Y %H:%M:%S %Z]", time.localtime()) + " Washer changed from stopped to running: {}".format(mysw_power))
                IS_RUNNING = 1
            else:
                print(time.strftime("[%d %b %Y %H:%M:%S %Z]", time.localtime()) + " Washer remains stopped: {}".format(mysw_power))
        else:
            if mysw_power < OFFPOWER:
                print(time.strftime("[%d %b %Y %H:%M:%S %Z]", time.localtime()) + " Washer changed from running to stopped: {}".format(mysw_power))
                triggerWebHook()
                IS_RUNNING = 0
            else:
                print(time.strftime("[%d %b %Y %H:%M:%S %Z]", time.localtime()) + " Washer remains running: {}".format(mysw_power))

        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()