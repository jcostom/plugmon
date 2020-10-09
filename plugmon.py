#!/usr/bin/env python3

import os
import time
import requests
from pyvesync_v2 import VeSync

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
TZ = os.getenv('TZ', 'America/New_York')
DEVID = int(os.getenv('DEVID', 0))
OFFPOWER = float(os.getenv('OFFPOWER', 0.2))
ONPOWER = float(os.getenv('ONPOWER', 0.8))

IFTTTKEY = os.getenv('IFTTTKEY')
IFTTTWEBHOOK = os.getenv('IFTTTWEBHOOK')

INTERVAL = os.getenv('INTERVAL', 300)

def triggerWebHook():
    webHookURL = "/".join(
        ("https://maker.ifttt.com/trigger",
        IFTTTWEBHOOK,
        "with/key",
        IFTTTKEY)
    )
    headers = {'User-Agent': 'plugmon.py v1.0'}
    response = requests.get(webHookURL, headers=headers)
    print(time.strftime("[%d %b %Y %H:%M:%S %Z]", time.localtime()) + " IFTTT Response: {}".format(response.text))

def main():
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